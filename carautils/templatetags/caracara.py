from django import template

from carautils.renderer import CaraCaraFormRenderer

register = template.Library()


@register.simple_tag
def render_form(serializer, template_pack=None):
    style = {'template_pack': template_pack} if template_pack else {}
    renderer = CaraCaraFormRenderer()
    return renderer.render(serializer.data, None, {'style': style})


@register.simple_tag
def render_field(field, style):
    renderer = style.get('renderer', CaraCaraFormRenderer())
    return renderer.render_field(field, style)
