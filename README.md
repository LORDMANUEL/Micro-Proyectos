# Suite de Micro-Proyectos

¡Bienvenido a esta colección de micro-proyectos! Cada proyecto está diseñado para ser una herramienta funcional y autocontenida, abordando un caso de uso específico.

---

## Proyectos en esta Colección

1.  [**Sistema FIFO de Tickets para TI**](#1-sistema-fifo-de-tickets-para-ti) *(Completado)*
2.  [**Analizador de Red con OSINT e IA**](#2-analizador-de-red-con-osint-e-ia) *(Completado)*
3.  [**Creador de Correos Profesionales con IA**](#3-creador-de-correos-profesionales-con-ia) *(Completado)*
4.  **Convertidor de Lenguaje Natural a SQL** *(Pendiente)*
5.  **Reproductor de Vídeos Minimalista** *(Pendiente)*
6.  **Compartidor de Archivos en Red Local** *(Pendiente)*
7.  **Sistema de Micro-Inventario de PCs** *(Pendiente)*
8.  **Plataforma de Gestión de Impresoras** *(Pendiente)*

---

## 1. Sistema FIFO de Tickets para TI

Este es un sistema de tickets simple y funcional, diseñado para equipos de TI. Permite a los clientes enviar solicitudes y al personal de TI **asignar, gestionar y cerrar** los tickets en una cola **FIFO (First-In, First-Out)**. El sistema cuenta con dos interfaces web distintas y utiliza IA para categorizar automáticamente los tickets.

![Captura de pantalla del Sistema de Tickets](https://i.imgur.com/L8a1j3f.png)

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

## 2. Analizador de Red con OSINT e IA

Esta herramienta proporciona un análisis de OSINT (Inteligencia de Fuentes Abiertas) para cualquier dirección IP. Simplemente introduce una IP y la aplicación recopilará datos de geolocalización, información del proveedor de servicios de internet (ISP) y registros WHOIS. Luego, utiliza IA para generar un resumen en lenguaje natural sobre el posible uso o tipo de dispositivo asociado a esa IP.

![Captura de pantalla del Analizador de Red](https://i.imgur.com/8aZ3j4M.png)

### ✨ Características Principales

-   **Análisis OSINT Completo:** Recopila geolocalización, datos del ISP y WHOIS.
-   **Resumen con IA:** Utiliza **Ollama** para interpretar los datos técnicos y ofrecer una conclusión fácil de entender.
-   **Interfaz Limpia y Reactiva:** La página muestra los resultados de forma organizada, con un indicador de carga mientras se realiza el análisis.
-   **Diseño Coherente:** Mantiene el estilo neumorfista con **Tailwind CSS** del resto de la suite.
-   **Instalación Modular:** Incluye su propio script de instalación que se integra con el entorno virtual principal.

### 🛠️ Stack Tecnológico

-   **Backend:** Python con **Flask**.
-   **Frontend:** HTML, CSS y JavaScript.
-   **Librerías Clave:** `requests` (para APIs externas) y `python-whois`.
-   **IA:** Integración con **Ollama** para la generación de resúmenes.

### 🚀 Instalación y Ejecución

#### Prerrequisitos

-   Haber instalado el primer proyecto (`Sistema de Tickets`) para tener el entorno virtual principal.

#### Pasos de Instalación

1.  **Dale permisos de ejecución** al script de instalación:
    ```bash
    chmod +x network_analyzer/install.sh
    ```
2.  **Ejecuta el script**:
    ```bash
    ./network_analyzer/install.sh
    ```
    Este script instalará las dependencias específicas de este proyecto dentro del entorno virtual ya existente.

#### Cómo Iniciar la Aplicación

1.  **Activa el entorno virtual** (desde la raíz del repositorio):
    ```bash
    source venv/bin/activate
    ```
2.  **Inicia el servidor de Flask**:
    ```bash
    python3 -m flask --app network_analyzer.backend.app run
    ```
3.  **Accede a la aplicación**:
    -   Abre tu navegador y ve a `http://127.0.0.1:5001/`

---

## 3. Creador de Correos Profesionales con IA

Esta herramienta te ayuda a redactar correos electrónicos profesionales en segundos. Simplemente proporciona el contexto: a quién va dirigido, cuál es el objetivo, el tono deseado y los puntos clave a incluir. La IA se encargará de generar un borrador de correo coherente y bien estructurado, listo para ser copiado y utilizado.

![Captura de pantalla del Generador de Correos](https://i.imgur.com/placeholder.png) <!-- Placeholder image -->

### ✨ Características Principales

-   **Generación Basada en Contexto:** Define el destinatario, objetivo, tono y puntos clave para guiar a la IA.
-   **Interfaz Intuitiva:** Un formulario claro y conciso hace que sea muy fácil de usar.
-   **Copia Rápida:** Un botón de "Copiar" permite llevar el texto generado a tu cliente de correo con un solo clic.
-   **Diseño Coherente:** Mantiene el estilo neumorfista con **Tailwind CSS**.
-   **Manejo de Errores Inteligente:** Si la IA no está disponible, la aplicación genera un correo de ejemplo para que la interfaz siga siendo funcional.

### 🛠️ Stack Tecnológico

-   **Backend:** Python con **Flask**.
-   **Frontend:** HTML, CSS y JavaScript.
-   **IA:** Integración con **Ollama** para la generación de texto.

### 🚀 Instalación y Ejecución

#### Prerrequisitos

-   Haber instalado el primer proyecto (`Sistema de Tickets`) para tener el entorno virtual principal.

#### Pasos de Instalación

1.  **Dale permisos de ejecución** al script de instalación:
    ```bash
    chmod +x email_generator/install.sh
    ```
2.  **Ejecuta el script**:
    ```bash
    ./email_generator/install.sh
    ```
    Este script instalará las dependencias de este proyecto en el entorno virtual existente.

#### Cómo Iniciar la Aplicación

1.  **Activa el entorno virtual** (desde la raíz del repositorio):
    ```bash
    source venv/bin/activate
    ```
2.  **Inicia el servidor de Flask**:
    ```bash
    python3 -m flask --app email_generator.backend.app run
    ```
3.  **Accede a la aplicación**:
    -   Abre tu navegador y ve a `http://127.0.0.1:5002/`

---
*Las secciones para los próximos proyectos se completarán a medida que se desarrollen.*
