from jinja2 import Environment, FileSystemLoader
import os

def render_recipe_to_html(recipe_data, template_name, output_path, extra_context=None):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)

    context = {
        "recipe": recipe_data,
    }

    if extra_context:
        context.update(extra_context)

    rendered_html = template.render(context)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"Generated: {output_path}")
