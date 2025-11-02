# Suite de Micro-Proyectos

¡Bienvenido a esta colección de micro-proyectos! Cada proyecto está diseñado para ser una herramienta funcional y autocontenida, abordando un caso de uso específico.

---

## Proyectos en esta Colección

1.  [**Sistema FIFO de Tickets para TI**](#1-sistema-fifo-de-tickets-para-ti) *(Completado)*
2.  **Analizador de Red con OSINT e IA** *(Pendiente)*
3.  **Creador de Correos Profesionales con IA** *(Pendiente)*
4.  **Convertidor de Lenguaje Natural a SQL** *(Pendiente)*
5.  **Reproductor de Vídeos Minimalista** *(Pendiente)*
6.  **Compartidor de Archivos en Red Local** *(Pendiente)*
7.  **Sistema de Micro-Inventario de PCs** *(Pendiente)*
8.  **Plataforma de Gestión de Impresoras** *(Pendiente)*

---

## 1. Sistema FIFO de Tickets para TI

Este es un sistema de tickets simple y ligero, diseñado para equipos de TI. Permite a los clientes enviar solicitudes de soporte y al personal de TI gestionarlas en una cola **FIFO (First-In, First-Out)**. El sistema cuenta con dos interfaces web distintas y utiliza IA para categorizar automáticamente los tickets.

### ✨ Características Principales

-   **Dos Interfaces Web:**
    -   Una página limpia y moderna para que los **clientes** envíen tickets.
    -   Un panel de control para que el **personal de TI** visualice la cola de tickets.
-   **Cola FIFO:** Los tickets se muestran en orden cronológico, del más antiguo al más nuevo.
-   **Categorización con IA:** Utiliza **Ollama** para analizar el contenido de los tickets y asignarles una categoría (`Hardware`, `Software`, `Red`, `Otro`) de forma automática y en segundo plano.
-   **Diseño Neumorfista:** La interfaz ha sido diseñada con un estilo neumorfista utilizando **Tailwind CSS**, dándole un aspecto suave y moderno.
-   **Instalación Sencilla:** Un script `install.sh` automatiza toda la configuración en sistemas **Debian/Ubuntu**.

### 🛠️ Stack Tecnológico

-   **Backend:** Python con el micro-framework **Flask**.
-   **Base de Datos:** **SQLite** para una configuración simple y sin dependencias externas.
-   **Frontend:** HTML, CSS y JavaScript.
-   **Estilos:** **Tailwind CSS** para un diseño rápido y moderno.
-   **IA:** Integración con **Ollama** para el procesamiento de lenguaje natural.

### 🚀 Instalación y Ejecución

#### Prerrequisitos

-   Un sistema operativo Debian o Ubuntu.
-   Acceso a `sudo` para instalar paquetes.

#### Pasos de Instalación

1.  **Clona el repositorio** (si aún no lo has hecho).
2.  **Dale permisos de ejecución** al script de instalación:
    ```bash
    chmod +x ticket_system/install.sh
    ```
3.  **Ejecuta el script**:
    ```bash
    ./ticket_system/install.sh
    ```
    El script se encargará de instalar Python, Pip, crear un entorno virtual, instalar las dependencias y inicializar la base de datos.

#### Cómo Iniciar la Aplicación

1.  **Activa el entorno virtual**:
    ```bash
    source venv/bin/activate
    ```
2.  **Inicia el servidor de Flask**:
    ```bash
    python3 -m flask --app ticket_system.backend.app run
    ```
3.  **Accede a las interfaces**:
    -   **Portal del Cliente:** Abre tu navegador y ve a `http://127.0.0.1:5000/`
    -   **Panel de Control de TI:** Abre tu navegador y ve a `http://127.0.0.1:5000/it`

### 🧠 Configuración de la IA (Ollama)

Para que la categorización automática funcione, el sistema necesita conectarse a una instancia de Ollama.

-   Asegúrate de tener **Ollama instalado y en ejecución**.
-   Verifica que el modelo que deseas usar (por defecto `llama2`) esté disponible.
-   Puedes configurar la URL de la API y el modelo a través de variables de entorno:
    ```bash
    export OLLAMA_API_URL="http://localhost:11434/api/generate"
    export OLLAMA_MODEL="llama2" # o el modelo que prefieras
    ```
---
*Las secciones para los próximos proyectos se completarán a medida que se desarrollen.*
