{#
  Map dbt's custom +schema (staging / marts) straight onto the BigQuery dataset
  of the same name, instead of dbt's default "<target>_<custom>" prefixing.
  This lines models up with the Terraform-provisioned raw / staging / marts datasets.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
