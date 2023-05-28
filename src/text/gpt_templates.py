DEFAULT_TEMPLATE = f"""[[main_idea]]
Provide json having ${{n}} fields:
${{arg1}} 
in the following format:
{{
    "${{arg2}}": ${{arg3}}
}}
Your response should contain only json. Json must be valid.
"""

ES_DEFAULT_TEMPLATE = f"""[[main_idea]]
Proporcione un json que tenga ${{n}} campos:
${{arg1}}
en el siguiente formato:
{{
"${{arg2}}": ${{arg3}}
}}
Tu respuesta solo debe contener json. El json debe ser válido.
"""

GPT_TEMPLATES = {
    "en": DEFAULT_TEMPLATE,
    "es": ES_DEFAULT_TEMPLATE
}