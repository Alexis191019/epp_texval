# Guía: Trabajar con la rama dev en la Jetson Orin Nano

## Flujo de trabajo general

```
Tu PC ──(git push)──> GitHub (rama dev) ──(git pull)──> Jetson Orin Nano
                                                              │
                                                              │ (cuando funciona)
                                                              ▼
                                                        Git Merge ──> master
```

---

## Paso 1: Clonar la rama dev en la Jetson (PRIMERA VEZ)

### 1. Clonar el repositorio completo

```bash
git clone https://github.com/Alexis191019/epp_texval.git
```

### 2. Entrar al directorio

```bash
cd epp_texval
```

### 3. Cambiar a la rama dev

```bash
git checkout dev
```

### 4. Verificar que estás en la rama dev

```bash
git branch
```

Deberías ver `* dev` (el asterisco indica la rama actual).

---

## Paso 2: Configurar el remote (VERIFICAR)

Después de clonar, verifica el remote:

```bash
git remote -v
```

Deberías ver:
```
origin  https://github.com/Alexis191019/epp_texval.git (fetch)
origin  https://github.com/Alexis191019/epp_texval.git (push)
```

Si no aparece, agrégalo:

```bash
git remote add origin https://github.com/Alexis191019/epp_texval.git
```

---

## Paso 3: Flujo de trabajo diario

### 🔧 En tu PC (donde haces cambios)

1. **Hacer cambios en tu código**

2. **Agregar cambios:**
   ```bash
   git add .
   ```

3. **Hacer commit:**
   ```bash
   git commit -m "Descripción de los cambios"
   ```

4. **Subir a GitHub (rama dev):**
   ```bash
   git push origin dev
   ```

### 📥 En la Jetson (cuando quieras actualizar)

1. **Verificar que estás en la rama dev:**
   ```bash
   git branch
   ```
   Debe mostrar `* dev`.

2. **Actualizar con los cambios de GitHub:**
   ```bash
   git pull origin dev
   ```
   Esto descarga y aplica los cambios nuevos automáticamente.

3. **Si hay conflictos (raro si solo trabajas desde tu PC):**
   - Git te avisará si hay conflictos
   - Resuélvelos según las instrucciones que Git te dé

---

## Paso 4: Fusionar dev a master (cuando funcione en Jetson)

Una vez que todo funciona correctamente en la Jetson, fusiona `dev` a `master`:

### 🔄 Desde tu PC:

```bash
# 1. Asegúrate de tener los últimos cambios en dev
git checkout dev
git pull origin dev

# 2. Cambiar a master
git checkout master

# 3. Fusionar dev en master
git merge dev

# 4. Subir master a GitHub
git push origin master
```

---

## Comandos útiles en la Jetson

### Ver el estado del repositorio:
```bash
git status
```

### Ver qué rama estás usando:
```bash
git branch
```

### Ver los últimos commits:
```bash
git log --oneline -5
```

### Deshacer cambios locales (si algo sale mal):
```bash
git reset --hard origin/dev
```
⚠️ **PRECAUCIÓN:** Esto borra todos los cambios locales no guardados.

---

## Conceptos importantes

### `git pull` vs `git fetch`
- **`git pull`**: Descarga cambios Y los fusiona automáticamente en tu código local
- **`git fetch`**: Solo descarga los cambios, pero NO los fusiona

Para actualizar la Jetson, usa: `git pull origin dev`

### `git checkout` vs `git clone`
- **`git clone`**: Crea una copia completa del repositorio (solo una vez, la primera vez)
- **`git checkout`**: Cambia de rama dentro del mismo repositorio

### Remote `origin`
- `origin` es el nombre por defecto del repositorio remoto en GitHub
- `origin dev` significa: "la rama `dev` en el remote `origin`"

---

## Resumen del flujo completo

1. **PC:** Hacer cambios → `git add .` → `git commit -m "mensaje"` → `git push origin dev`
2. **Jetson:** `git pull origin dev` (actualiza con los cambios)
3. **Jetson:** Probar y verificar que funciona
4. **PC o GitHub:** Fusionar `dev` a `master` cuando esté listo

---

## Preguntas frecuentes

**¿Debo hacer commit en la Jetson?**
- No necesariamente. Puedes hacerlo solo en tu PC y actualizar la Jetson con `git pull`
- Si haces commits en la Jetson, usa `git push origin dev` para subirlos

**¿Qué pasa si hay conflictos?**
- Git te avisará si hay conflictos
- Resuelve los conflictos y luego `git add` y `git commit`

**¿Cómo sé si hay cambios nuevos?**
- `git status` te mostrará si estás actualizado o si hay cambios nuevos en el remoto

---

## Notas adicionales

- La rama `dev` es para desarrollo/pruebas
- La rama `master` es para código estable/funcional
- Siempre prueba en `dev` antes de fusionar a `master`
