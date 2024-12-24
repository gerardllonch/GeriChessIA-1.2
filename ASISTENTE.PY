import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
import config

"""
- Documentación API ChatGPT: https://platform.openai.com/docs/api-reference/chat
"""

def main():

    try:
        openai.api_key = config.api_key  #"TU_API_KEY creada en https://platform.openai.com"
    except AttributeError:
        print("[bold red]Error:[/bold red] No se ha encontrado la API key en el archivo de configuración.")
        return

    print("💬 [bold green]Pregunta a la IA lo que quieras[/bold green]")

    table = ("exit = cerrar el chat")
    
    print(table)

    # Contexto del asistente
    context = {"role": "system",
               "content": "Eres un maestro de ajedrez"}
    messages = [context]

    while True:
        try:
            content = __prompt()

            if content == "exit":
                print("[bold blue]Saliendo del chat...[/bold blue]")
                break

            messages.append({"role": "user", "content": content})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=550  # Establece el límite de tokens en 550
            )

            response_content = response.choices[0].message.content

            messages.append({"role": "assistant", "content": response_content})

            print(f"[bold green]> [/bold green] [green]{response_content}[/green]")

        except openai.error.AuthenticationError:
            print("[bold red]Error de autenticación:[/bold red] Verifica tu API key.")
            break
        except openai.error.OpenAIError as e:
            print(f"[bold red]Error en la API de OpenAI:[/bold red] {str(e)}")
        except Exception as e:
            print(f"[bold red]Ha ocurrido un error inesperado:[/bold red] {str(e)}")

def __prompt() -> str:
    try:
        prompt = typer.prompt("\nSi lo necesitas hazme una pregunta ")
        return prompt
    except Exception as e:
        print(f"[bold red]Error al obtener entrada del usuario:[/bold red] {str(e)}")
        return "exit"

if __name__ == "__main__":
    try:
        typer.run(main)
    except Exception as e:
        print(f"[bold red]Error inesperado al ejecutar la aplicación:[/bold red] {str(e)}")