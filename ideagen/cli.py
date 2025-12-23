import click
import logging
from ideagen.pipeline import Pipeline

@click.command()
@click.argument('topic')
@click.option('-n', '--num-ideas', default=10, show_default=True, help='Number of ideas to generate')
@click.option('--output', default=None, help='Output JSON file path')
@click.option('--scores-output', default=None, help='Optional scores JSON output path')
@click.option('--model', default='openai/gpt-4.1-nano', show_default=True, help='Model name')
@click.option('--skip-dedupe', is_flag=True, help='Skip deduplication step')
@click.option('--skip-score', is_flag=True, help='Skip scoring step')
@click.option('--generation-prompt', default=None, type=click.Path(exists=True), help='Custom generation prompt file')
@click.option('--evaluation-prompt', default=None, type=click.Path(exists=True), help='Custom evaluation prompt file')
def main(topic, num_ideas, output, scores_output, model, skip_dedupe, skip_score, generation_prompt, evaluation_prompt):
    logging.basicConfig(level=logging.INFO)
    gen_prompt = None
    eval_prompt = None
    if generation_prompt:
        with open(generation_prompt, 'r') as f:
            gen_prompt = f.read()
    if evaluation_prompt:
        with open(evaluation_prompt, 'r') as f:
            eval_prompt = f.read()
    pipeline = Pipeline(model_name=model)
    results = pipeline.run(
        topic=topic,
        num_ideas=num_ideas,
        output_path=output,
        generation_prompt=gen_prompt,
        evaluation_prompt=eval_prompt,
        skip_dedupe=skip_dedupe,
        skip_score=skip_score,
        scores_output_path=scores_output
    )
    click.echo(f"Generated {len(results.ideas)} ideas.")
    if output:
        click.echo(f"Results saved to {output}")
    if scores_output and not skip_score:
        click.echo(f"Scores saved to {scores_output}")

if __name__ == '__main__':
    main()
