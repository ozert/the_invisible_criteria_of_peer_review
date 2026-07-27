import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

TASK_PATH = "data/artifacts/study_a_task.json"
console = Console()

TOPICS = """
[bold cyan]TOPICS:[/bold cyan]
0: Methodology          7: Performance & Metrics
1: Comparative Analysis 8: Validity & Reproducibility
2: Applicability/Limits 9: Data
3: Theoretical Found.   10: Motivation & Contribution
4: Terminology/Clarity  11: Computational Efficiency
5: Presentation/Figures 12: Ethical Considerations
6: Interpretability     13: [red]UNSURE / OTHER[/red]
"""

def load(): return json.load(open(TASK_PATH, encoding="utf-8"))
def save(data): json.dump(data, open(TASK_PATH, "w", encoding="utf-8"), indent=2)

def run():
    data = load()
    task = data["task"]
    
    # Find first review that hasn't been marked as "done"
    # We use a special flag "_done" to know if you finished a review (even if it has 0 chunks)
    i = next((k for k, t in enumerate(task) if not t.get("_done")), 0)

    while 0 <= i < len(task):
        t = task[i]
        console.clear()
        
        title = f" Review {i+1}/{len(task)} | ID: {t['review_id']} | Rating: {t['rating']} "
        console.print(Panel(f"[bold yellow]{t['raw_questions']}[/bold yellow]", title=title))
        console.print(TOPICS)
        
        if t["human_chunks"]:
            console.print("\n[bold green]Chunks extracted so far:[/bold green]")
            for idx, c in enumerate(t["human_chunks"]):
                console.print(f"  {idx+1}. (Topic {c['topic']}) {c['text'][:60]}...")
        
        console.print("\n[bold]Options:[/bold] [green]'a'[/green]=Add Chunk | [yellow]'d'[/yellow]=Done with Review | [red]'u'[/red]=Undo Last | [blue]'q'[/blue]=Quit")
        act = Prompt.ask("Action", choices=["a", "d", "u", "q"], default="a")
        
        if act == "a":
            chunk_text = Prompt.ask("\n[cyan]Paste/Type the question chunk[/cyan]")
            topic = Prompt.ask("[cyan]Topic ID (0-13)[/cyan]", choices=[str(x) for x in range(14)])
            t["human_chunks"].append({"text": chunk_text, "topic": int(topic)})
            save(data)
        elif act == "u":
            if t["human_chunks"]:
                t["human_chunks"].pop()
                save(data)
        elif act == "d":
            # Automatically label as non-informative if no chunks were extracted
            if len(t.get("human_chunks", [])) == 0:
                t["non_informative"] = True
            else:
                t["non_informative"] = False
                
            t["_done"] = True
            save(data)
            i += 1
        elif act == "q":
            break

    console.clear()
    console.print("[bold green]Saved. Exiting.[/bold green]")

if __name__ == "__main__":
    run()