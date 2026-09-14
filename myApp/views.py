from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F, Avg
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Curso, Profesor, Estudiante, Entregable, Entrega, Inscripcion, Nota, RegistroAsistencia, Resena
from .forms import CursoForm, ProfesorFormulario, ProfesorForm, EstudianteFormulario, EstudianteForm, EntregableForm, InscripcionForm, NotaForm, ResenaForm, RegistroEstudianteForm
from .decorators import admin_required, profesor_required, es_administrador


def _entregables_info_de_curso(curso, inscripciones):
    total_alumnos = inscripciones.count()
    resultado = []
    for entregable in Entregable.objects.filter(curso=curso).order_by('id'):
        entregados_ids = set(
            Entrega.objects.filter(entregable=entregable, estudiante__inscripciones__curso=curso)
            .values_list('estudiante_id', flat=True)
        )
        detalle = [
            {'estudiante': inscripcion.estudiante, 'entrego': inscripcion.estudiante_id in entregados_ids}
            for inscripcion in inscripciones
        ]
        cantidad = len(entregados_ids)
        porcentaje = round((cantidad / total_alumnos) * 100) if total_alumnos > 0 else 0
        resultado.append({
            'entregable': entregable,
            'cantidad_entregados': cantidad,
            'total_alumnos': total_alumnos,
            'porcentaje': porcentaje,
            'detalle': detalle,
        })
    return resultado


def _recalcular_promedio(inscripcion):
    promedio = inscripcion.notas.aggregate(promedio=Avg('nota'))['promedio']
    inscripcion.promedio = round(promedio, 1) if promedio is not None else 0.0
    inscripcion.save(update_fields=['promedio'])

# 0. Vistas de autenticación

def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            error = "Usuario o contraseña incorrectos."

    return render(request, 'myApp/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('myapp:login')


# NUEVO: Autorregistro del estudiante (documento = usuario)
def registro_estudiante(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
       
        
        if form.is_valid():
            documento = form.cleaned_data['documento']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=documento,
                        password=password,
                        email=email
                    )
                    Estudiante.objects.create(
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        email=email,
                        documento=documento,
                        asistencia=0,
                        promedio=0.0,
                        proyectos_hechos=0,
                        proyectos_totales=0,
                        user=user,
                    )
                messages.success(request, "¡Cuenta creada con éxito! Ya podés iniciar sesión con tu documento y tu contraseña.")
                return redirect('myapp:login')
            except Exception as e:
                messages.error(request, f"Error al crear la cuenta: {str(e)}")
                return render(request, 'myApp/register.html', {'form': form})
    else:
        form = RegistroEstudianteForm()

    return render(request, 'myApp/register.html', {'form': form})


# 1. Vista de inicio (MODIFICADA PARA MANEJAR LOS 3 ROLES)

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'myApp/welcome.html')
    
    # Si es administrador, va al panel de admin
    if es_administrador(request.user):
        context = {
            "total_cursos": Curso.objects.count(),
            "total_estudiantes": Estudiante.objects.count(),
            "total_profesores": Profesor.objects.count(),
        }
        return render(request, 'myApp/index.html', context)
    
    # Si es profesor, va al panel de profesor
    if hasattr(request.user, 'profesor'):
        return redirect('myapp:mis_cursos')
    
    # Si es estudiante, va al panel de estudiante
    if hasattr(request.user, 'estudiante'):
        return redirect('myapp:mis_cursos_estudiante')
    
    # Si no tiene ningún perfil, cerrar sesión
    messages.warning(request, "No tienes un perfil asignado. Contacta al administrador.")
    auth_logout(request)
    return redirect('myapp:login')

# 2. Vista para buscar cursos
@login_required
def buscar_curso(request):
    if request.GET.get('camada'):
        camada = request.GET['camada']
        cursos = Curso.objects.filter(camada__icontains=camada)
        return render(request, 'myApp/resultados_busqueda.html', {'cursos': cursos, 'camada': camada})
    return render(request, 'myApp/buscar_curso.html') 

# 3. Vista para listar los cursos
@login_required
def lista_cursos(request):
    if es_administrador(request.user):
        cursos = Curso.objects.all()
    else:
        cursos = Curso.objects.filter(profesores__user=request.user)
    cursos = cursos.prefetch_related('profesores', 'inscripciones')
    return render(request, 'myApp/cursos_list.html', {'cursos': cursos})

@admin_required
def lista_estudiantes(request):
    query = request.GET.get('q', '').strip()
    estudiantes = Estudiante.objects.all().order_by('nombre', 'apellido')
    if query:
        estudiantes = estudiantes.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )
    total_estudiantes = estudiantes.count()
    paginator = Paginator(estudiantes, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'myApp/estudiantes_list.html', {
        'estudiantes': page_obj,
        'query': query,
        'total_estudiantes': total_estudiantes,
    })

@admin_required
def detalle_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    inscripciones = estudiante.inscripciones.select_related('curso').all()
    return render(request, 'myApp/estudiante_detail.html', {'estudiante': estudiante, 'inscripciones': inscripciones})

@admin_required
def profesores(request):
    query = request.GET.get('q')
    if query:
        profesores = Profesor.objects.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(profesion__icontains=query)
        )
    else:
        profesores = Profesor.objects.all()
    return render(request, 'myApp/profesores.html', {'profesores': profesores, 'query': query})


@admin_required
def profesorFormulario(request):
    if request.method == 'POST':
        form = ProfesorFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            # Verificar que el username no exista ya
            if User.objects.filter(username=username).exists():
                messages.error(request, f"El nombre de usuario '{username}' ya está en uso. Elegí otro.")
                return render(request, 'myApp/profesor_formulario.html', {'form': form})

            try:
                with transaction.atomic():
                    # Crear el usuario de Django
                    user = User.objects.create_user(
                        username=username, 
                        password=password, 
                        email=email
                    )

                    # Crear el Profesor y vincularlo al usuario
                    Profesor.objects.create(
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        email=email,
                        profesion=form.cleaned_data['profesion'],
                        user=user
                    )

                messages.success(request, f"¡Profesor creado exitosamente! Usuario: {username} - Contraseña: {password}")
                return redirect('myapp:profesores')
            except Exception as e:
                messages.error(request, f"Error al crear el profesor: {str(e)}")
                return render(request, 'myApp/profesor_formulario.html', {'form': form})
    else:
        form = ProfesorFormulario()
    return render(request, 'myApp/profesor_formulario.html', {'form': form})

@admin_required
def profesor_editar(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, instance=profesor)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_email = form.cleaned_data.get('user_email', '')
            new_password = form.cleaned_data.get('new_password', '')

            # Verificar que el username no esté en uso por otro usuario
            if User.objects.filter(username=username).exclude(pk=profesor.user.pk if hasattr(profesor, 'user') else None).exists():
                messages.error(request, f"El nombre de usuario '{username}' ya está en uso. Elegí otro.")
                return render(request, 'myApp/profesor_editar.html', {'form': form, 'profesor': profesor})

            try:
                with transaction.atomic():
                    # Guardar datos del profesor
                    profesor = form.save()

                    # Actualizar datos del usuario de Django
                    if hasattr(profesor, 'user'):
                        user = profesor.user
                        user.username = username
                        user.email = user_email

                        # Si se ingresó una nueva contraseña, actualizarla
                        if new_password:
                            if len(new_password) < 8:
                                messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
                                return render(request, 'myApp/profesor_editar.html', {'form': form, 'profesor': profesor})
                            user.set_password(new_password)

                        user.save()
                    else:
                        # Si no tiene usuario vinculado, crear uno nuevo
                        user = User.objects.create_user(
                            username=username,
                            password=new_password if new_password else 'temporal123',
                            email=user_email
                        )
                        profesor.user = user
                        profesor.save()

                messages.success(request, "Profesor actualizado correctamente.")
                return redirect('myapp:profesores')
            except Exception as e:
                messages.error(request, f"Error al actualizar el profesor: {str(e)}")
                return render(request, 'myApp/profesor_editar.html', {'form': form, 'profesor': profesor})
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'myApp/profesor_editar.html', {'form': form, 'profesor': profesor})

@admin_required
def profesor_eliminar(request, id):
    profesor = get_object_or_404(Profesor, id=id)
    if request.method == 'POST':
        profesor.delete()
        messages.success(request, "Profesor eliminado correctamente.")
        return redirect('myapp:profesores')
    return render(request, 'myApp/profesor_confirm_delete.html', {'profesor': profesor})

@admin_required
def estudianteFormulario(request):
    if request.method == 'POST':
        form = EstudianteFormulario(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            # Verificar que el username no exista ya
            if User.objects.filter(username=username).exists():
                messages.error(request, f"El nombre de usuario '{username}' ya está en uso. Elegí otro.")
                return render(request, 'myApp/estudiante_formulario.html', {'form': form})

            try:
                with transaction.atomic():
                    # Crear el usuario de Django
                    user = User.objects.create_user(
                        username=username, 
                        password=password, 
                        email=email
                    )

                    # Crear el Estudiante y vincularlo al usuario
                    Estudiante.objects.create(
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        email=email,
                        asistencia=0,
                        promedio=0.0,
                        proyectos_hechos=0,
                        proyectos_totales=0,
                        user=user
                    )

                messages.success(request, f"¡Estudiante creado exitosamente! Usuario: {username} - Contraseña: {password}")
                return redirect('myapp:estudiantes')
            except Exception as e:
                messages.error(request, f"Error al crear el estudiante: {str(e)}")
                return render(request, 'myApp/estudiante_formulario.html', {'form': form})
    else:
        form = EstudianteFormulario()
    return render(request, 'myApp/estudiante_formulario.html', {'form': form})

@admin_required
def estudiante_editar(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, "Estudiante actualizado correctamente.")
            return redirect('myapp:estudiantes')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'myApp/estudiante_editar.html', {'form': form, 'estudiante': estudiante})

@admin_required
def estudiante_eliminar(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        estudiante.delete()
        messages.success(request, "Estudiante eliminado correctamente.")
        return redirect('myapp:estudiantes')
    return render(request, 'myApp/estudiante_confirm_delete.html', {'estudiante': estudiante})

@login_required
@profesor_required
def entregable_editar(request, id):
    entregable = get_object_or_404(Entregable, id=id, curso__profesores__user=request.user)
    curso = entregable.curso

    if request.method == 'POST':
        form = EntregableForm(request.POST, request.FILES, instance=entregable)
        if form.is_valid():
            form.save()
            messages.success(request, "Entregable actualizado correctamente.")
            return redirect('myapp:curso_entregables', id=curso.id)
    else:
        form = EntregableForm(instance=entregable)
    return render(request, 'myApp/entregable_editar.html', {'form': form, 'entregable': entregable, 'curso': curso})

@login_required
@profesor_required
def entregable_ver(request, id):
    entregable = get_object_or_404(Entregable, id=id, curso__profesores__user=request.user)
    curso = entregable.curso
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante').order_by('estudiante__nombre', 'estudiante__apellido')
    entregas_por_estudiante = {
        e.estudiante_id: e for e in Entrega.objects.filter(entregable=entregable)
    }

    filas = []
    a_tiempo = 0
    fuera_de_termino = 0
    no_entrego = 0
    for inscripcion in inscripciones:
        entrega = entregas_por_estudiante.get(inscripcion.estudiante_id)
        if entrega:
            es_a_tiempo = not entregable.fecha_vencimiento or entrega.fecha_entrega <= entregable.fecha_vencimiento
            if es_a_tiempo:
                a_tiempo += 1
            else:
                fuera_de_termino += 1
        else:
            no_entrego += 1
        filas.append({
            'estudiante': inscripcion.estudiante,
            'entrega': entrega,
            'a_tiempo': entrega and es_a_tiempo,
        })

    return render(request, 'myApp/entregable_ver.html', {
        'curso': curso,
        'entregable': entregable,
        'filas': filas,
        'total_alumnos': len(filas),
        'a_tiempo': a_tiempo,
        'fuera_de_termino': fuera_de_termino,
        'no_entrego': no_entrego,
    })

@login_required
@profesor_required
def entrega_calificar(request, id):
    entrega = get_object_or_404(Entrega, id=id, entregable__curso__profesores__user=request.user)
    entregable = entrega.entregable
    curso = entregable.curso
    if request.method == 'POST':
        valor = request.POST.get('nota', '').replace(',', '.').strip()
        try:
            nota_valor = float(valor)
        except ValueError:
            nota_valor = None
        if nota_valor is None or nota_valor < 1 or nota_valor > 10:
            messages.error(request, "La nota debe ser un número entre 1 y 10.")
        else:
            inscripcion = get_object_or_404(Inscripcion, estudiante=entrega.estudiante, curso=curso)
            entrega.nota = nota_valor
            entrega.save(update_fields=['nota'])
            Nota.objects.update_or_create(
                entrega=entrega,
                defaults={
                    'inscripcion': inscripcion,
                    'nombre': entregable.nombre,
                    'tipo': Nota.TIPO_ENTREGABLE,
                    'fecha': entrega.fecha_entrega.date() if entrega.fecha_entrega else None,
                    'nota': nota_valor,
                }
            )
            _recalcular_promedio(inscripcion)
            messages.success(request, "Nota guardada y agregada a los datos académicos del alumno.")
    return redirect('myapp:entregableVer', id=entregable.id)

@login_required
@profesor_required
def entregable_eliminar(request, id):
    entregable = get_object_or_404(Entregable, id=id, curso__profesores__user=request.user)
    curso = entregable.curso
    if request.method == 'POST':
        with transaction.atomic():
            estudiantes_que_entregaron = list(
                Estudiante.objects.filter(entregas__entregable=entregable, inscripciones__curso=curso)
            )
            if estudiantes_que_entregaron:
                Inscripcion.objects.filter(
                    curso=curso, estudiante__in=estudiantes_que_entregaron
                ).update(proyectos_hechos=F('proyectos_hechos') - 1)
                Inscripcion.objects.filter(
                    curso=curso, proyectos_hechos__lt=0
                ).update(proyectos_hechos=0)

            entregable.delete()

            Inscripcion.objects.filter(curso=curso).update(proyectos_totales=F('proyectos_totales') - 1)
            Inscripcion.objects.filter(curso=curso, proyectos_totales__lt=0).update(proyectos_totales=0)

        messages.success(request, "Entregable eliminado correctamente.")
        return redirect('myapp:curso_entregables', id=curso.id)
    return render(request, 'myApp/entregable_confirm_delete.html', {'entregable': entregable, 'curso': curso})



@admin_required
def cursoFormulario(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                curso = form.save(commit=False)
                curso.save()
                form.save_m2m()  # guarda curso.profesores

                alumnos_seleccionados = form.cleaned_data['alumnos']
                proyectos_totales_inicial = Entregable.objects.filter(curso=curso).count()
                for estudiante in alumnos_seleccionados:
                    Inscripcion.objects.create(
                        estudiante=estudiante,
                        curso=curso,
                        asistencia=0,
                        promedio=0,
                        proyectos_hechos=0,
                        proyectos_totales=proyectos_totales_inicial,
                    )
            messages.success(request, "Curso agregado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoForm()
    return render(request, 'myApp/curso_form.html', {'form': form})

@admin_required
def curso_editar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            with transaction.atomic():
                form.save()  # guarda nombre, camada y curso.profesores

                alumnos_seleccionados = set(form.cleaned_data['alumnos'])
                alumnos_actuales = set(Estudiante.objects.filter(inscripciones__curso=curso))

                nuevos = alumnos_seleccionados - alumnos_actuales
                quitados = alumnos_actuales - alumnos_seleccionados

                proyectos_totales_inicial = Entregable.objects.filter(curso=curso).count()
                for estudiante in nuevos:
                    Inscripcion.objects.create(
                        estudiante=estudiante,
                        curso=curso,
                        asistencia=0,
                        promedio=0,
                        proyectos_hechos=0,
                        proyectos_totales=proyectos_totales_inicial,
                    )

                if quitados:
                    Inscripcion.objects.filter(curso=curso, estudiante__in=quitados).delete()

            messages.success(request, "Curso actualizado correctamente.")
            return redirect('myapp:cursos')
    else:
        form = CursoForm(instance=curso, initial={
            'alumnos': Estudiante.objects.filter(inscripciones__curso=curso),
        })
    return render(request, 'myApp/curso_editar.html', {'form': form, 'curso': curso})

@admin_required
def admin_curso_detail(request, id):
    curso = get_object_or_404(Curso, id=id)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')
    return render(request, 'myApp/admin_curso_detail.html', {
        'curso': curso,
        'inscripciones': inscripciones,
    })

@login_required
@admin_required
def admin_estudiante_curso_eliminar(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        nombre_estudiante = str(inscripcion.estudiante)
        inscripcion.delete()
        messages.success(request, f"{nombre_estudiante} fue dado de baja de {curso.nombre}.")
        return redirect('myapp:cursoDetalleAdmin', id=curso.id)
    return render(request, 'myApp/admin_estudiante_curso_confirm_delete.html', {
        'curso': curso,
        'inscripcion': inscripcion,
    })

@admin_required
def curso_eliminar(request, id):
    curso = get_object_or_404(Curso, id=id)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, "Curso eliminado correctamente.")
        return redirect('myapp:cursos')
    return render(request, 'myApp/curso_confirm_delete.html', {'curso': curso})


# ==========================================
# VISTA DE RESEÑAS PARA EL ADMIN (CON COMENTARIOS)
# ==========================================

@admin_required
def admin_curso_resenas(request, id):
    """Vista para que el admin vea TODAS las reseñas de un curso (con comentarios)."""
    curso = get_object_or_404(Curso, id=id)
    resenas = Resena.objects.filter(curso=curso).select_related('estudiante').order_by('-fecha')
    
    # Calcular estadísticas
    total_resenas = resenas.count()
    
    if total_resenas > 0:
        promedio = sum(r.calificacion for r in resenas) / total_resenas
        distribucion = {
            5: resenas.filter(calificacion=5).count(),
            4: resenas.filter(calificacion=4).count(),
            3: resenas.filter(calificacion=3).count(),
            2: resenas.filter(calificacion=2).count(),
            1: resenas.filter(calificacion=1).count(),
        }
    else:
        promedio = 0
        distribucion = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    return render(request, 'myApp/admin_curso_resenas.html', {
        'curso': curso,
        'resenas': resenas,
        'total_resenas': total_resenas,
        'promedio': round(promedio, 1),
        'distribucion': distribucion,
    })


# 4. Vistas del Profesor

@login_required
@profesor_required
def mis_cursos(request):
    cursos = Curso.objects.filter(profesores__user=request.user)
    return render(request, 'myApp/mis_cursos.html', {'cursos': cursos})

@login_required
@profesor_required
def curso_detail(request, id):
    curso = get_object_or_404(Curso, id=id, profesores__user=request.user)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')

    return render(request, 'myApp/curso_detail.html', {
        'curso': curso,
        'inscripciones': inscripciones,
    })

@login_required
@profesor_required
def curso_entregables(request, id):
    curso = get_object_or_404(Curso, id=id, profesores__user=request.user)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante')
    entregables_info = _entregables_info_de_curso(curso, inscripciones)

    return render(request, 'myApp/curso_entregables.html', {
        'curso': curso,
        'entregables_info': entregables_info,
    })

@login_required
@profesor_required
def tomar_asistencia(request, id):
    curso = get_object_or_404(Curso, id=id, profesores__user=request.user)
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related('estudiante').order_by('estudiante__nombre', 'estudiante__apellido')

    if request.method == 'POST':
        fecha = parse_date(request.POST.get('fecha', '')) or timezone.localdate()
        for inscripcion in inscripciones:
            presente = request.POST.get(f'presente_{inscripcion.id}') == 'on'
            RegistroAsistencia.objects.update_or_create(
                inscripcion=inscripcion, fecha=fecha, defaults={'presente': presente}
            )
        for inscripcion in inscripciones:
            total = inscripcion.registros_asistencia.count()
            presentes = inscripcion.registros_asistencia.filter(presente=True).count()
            inscripcion.asistencia = round((presentes / total) * 100) if total else 0
            inscripcion.save(update_fields=['asistencia'])
        messages.success(request, "Asistencia guardada correctamente.")
        return redirect(f"{request.path}?fecha={fecha.isoformat()}")

    fecha = parse_date(request.GET.get('fecha', '')) or timezone.localdate()

    filas = []
    for inscripcion in inscripciones:
        total = inscripcion.registros_asistencia.count()
        presentes = inscripcion.registros_asistencia.filter(presente=True).count()
        registro_dia = inscripcion.registros_asistencia.filter(fecha=fecha).first()
        presente_hoy = registro_dia.presente if registro_dia else True
        porcentaje = round((presentes / total) * 100) if total else 0
        filas.append({
            'inscripcion': inscripcion,
            'presente': presente_hoy,
            'total_clases': total,
            'porcentaje': porcentaje,
        })

    return render(request, 'myApp/tomar_asistencia.html', {
        'curso': curso,
        'fecha': fecha,
        'filas': filas,
    })

@login_required
@profesor_required
def estudiante_curso_eliminar(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id, profesores__user=request.user)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        nombre_estudiante = str(inscripcion.estudiante)
        inscripcion.delete()
        messages.success(request, f"{nombre_estudiante} fue dado de baja de {curso.nombre}.")
        return redirect('myapp:curso_detail', id=curso.id)
    return render(request, 'myApp/estudiante_curso_confirm_delete.html', {
        'curso': curso,
        'inscripcion': inscripcion,
    })

@login_required
@profesor_required
def inscripcion_editar(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id, profesores__user=request.user)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        form = InscripcionForm(request.POST, instance=inscripcion)
        if form.is_valid():
            form.save()
            messages.success(request, "Datos académicos actualizados correctamente.")
            return redirect('myapp:curso_detail', id=curso.id)
    else:
        form = InscripcionForm(instance=inscripcion)
    return render(request, 'myApp/inscripcion_editar.html', {
        'form': form,
        'curso': curso,
        'inscripcion': inscripcion,
        'notas': inscripcion.notas.order_by('id'),
        'nota_form': NotaForm(),
    })

@login_required
@profesor_required
def nota_crear(request, curso_id, estudiante_id):
    curso = get_object_or_404(Curso, id=curso_id, profesores__user=request.user)
    inscripcion = get_object_or_404(Inscripcion, curso=curso, estudiante_id=estudiante_id)
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.inscripcion = inscripcion
            nota.save()
            _recalcular_promedio(inscripcion)
            messages.success(request, "Nota agregada correctamente.")
        else:
            messages.error(request, "Revisá los datos de la nota: no se pudo agregar.")
    return redirect('myapp:inscripcionEditar', curso_id=curso.id, estudiante_id=inscripcion.estudiante_id)

@login_required
@profesor_required
def nota_editar(request, id):
    nota = get_object_or_404(Nota, id=id, inscripcion__curso__profesores__user=request.user)
    inscripcion = nota.inscripcion
    curso = inscripcion.curso
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            _recalcular_promedio(inscripcion)
            messages.success(request, "Nota actualizada correctamente.")
            return redirect('myapp:inscripcionEditar', curso_id=curso.id, estudiante_id=inscripcion.estudiante_id)
    else:
        form = NotaForm(instance=nota)
    return render(request, 'myApp/nota_editar.html', {
        'form': form,
        'nota': nota,
        'curso': curso,
        'inscripcion': inscripcion,
    })

@login_required
@profesor_required
def nota_eliminar(request, id):
    nota = get_object_or_404(Nota, id=id, inscripcion__curso__profesores__user=request.user)
    inscripcion = nota.inscripcion
    curso = inscripcion.curso
    if request.method == 'POST':
        nota.delete()
        _recalcular_promedio(inscripcion)
        messages.success(request, "Nota eliminada correctamente.")
    return redirect('myapp:inscripcionEditar', curso_id=curso.id, estudiante_id=inscripcion.estudiante_id)

@login_required
@profesor_required
def entregable_crear_en_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id, profesores__user=request.user)
    if request.method == 'POST':
        form = EntregableForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                entregable = form.save(commit=False)
                entregable.curso = curso
                entregable.cantidad_entregados = 0
                entregable.save()
                Inscripcion.objects.filter(curso=curso).update(proyectos_totales=F('proyectos_totales') + 1)
            messages.success(request, "Entregable agregado correctamente.")
            return redirect('myapp:curso_entregables', id=curso.id)
    else:
        form = EntregableForm()
    return render(request, 'myApp/entregable_crear_en_curso.html', {'form': form, 'curso': curso})


# ==========================================
# VISTA DE RESEÑAS PARA EL PROFESOR (SOLO PROMEDIO)
# ==========================================

@login_required
@profesor_required
def curso_resenas(request, id):
    """Vista para que el profesor vea SOLO el promedio de reseñas de su curso."""
    curso = get_object_or_404(Curso, id=id, profesores__user=request.user)
    resenas = Resena.objects.filter(curso=curso)
    
    # Calcular estadísticas
    total_resenas = resenas.count()
    
    if total_resenas > 0:
        promedio = sum(r.calificacion for r in resenas) / total_resenas
        distribucion = {
            5: resenas.filter(calificacion=5).count(),
            4: resenas.filter(calificacion=4).count(),
            3: resenas.filter(calificacion=3).count(),
            2: resenas.filter(calificacion=2).count(),
            1: resenas.filter(calificacion=1).count(),
        }
    else:
        promedio = 0
        distribucion = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    return render(request, 'myApp/curso_resenas.html', {
        'curso': curso,
        'total_resenas': total_resenas,
        'promedio': round(promedio, 1),
        'distribucion': distribucion,
    })


# ==========================================
# VISTAS PARA EL ESTUDIANTE
# ==========================================

@login_required
def mis_cursos_estudiante(request):
    """Panel donde el estudiante ve sus cursos inscriptos y sus estadísticas."""
    try:
        estudiante = request.user.estudiante
        inscripciones = Inscripcion.objects.filter(estudiante=estudiante).select_related('curso')
    except Estudiante.DoesNotExist:
        inscripciones = []
        messages.warning(request, "No tienes un perfil de estudiante vinculado. Contacta al administrador.")
    
    return render(request, 'myApp/mis_cursos_estudiante.html', {'inscripciones': inscripciones})

@login_required
def resena_crear(request, curso_id):
    """Vista para que el estudiante deje una reseña/opinión sobre un curso."""
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Verificar que el usuario sea un estudiante y esté inscripto
    try:
        estudiante = request.user.estudiante
        inscripcion = Inscripcion.objects.get(estudiante=estudiante, curso=curso)
    except (Estudiante.DoesNotExist, Inscripcion.DoesNotExist):
        messages.error(request, "No estás inscripto en este curso o no tienes perfil de estudiante.")
        return redirect('myapp:mis_cursos_estudiante')

    # Verificar que no haya reseñado ya este curso
    if Resena.objects.filter(estudiante=estudiante, curso=curso).exists():
        messages.warning(request, "Ya dejaste una opinión sobre este curso.")
        return redirect('myapp:mis_cursos_estudiante')

    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.estudiante = estudiante
            resena.curso = curso
            resena.save()
            messages.success(request, "¡Gracias por tu opinión! Tu reseña fue publicada.")
            return redirect('myapp:mis_cursos_estudiante')
    else:
        form = ResenaForm()

    return render(request, 'myApp/resena_form.html', {'form': form, 'curso': curso})