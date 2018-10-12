{%- extends 'basic.tpl' -%}

{% block body %}
<body>
   CONTENT
  <div tabindex="-1" id="notebook" class="border-box-sizing">
    <div class="container" id="notebook-container">
{{ super() }}
    </div>
  </div>
</body>
{%- endblock body %}
