shader_type canvas_item;
render_mode unshaded;
uniform sampler2D palette_texture : filter_nearest, repeat_disable;
uniform float palette_row = 0.0;
void fragment() {
 vec4 encoded = texture(TEXTURE, UV);
 float index = floor(encoded.r * 255.0 + 0.5);
 COLOR = texture(palette_texture, vec2((index + 0.5) / 16.0, (palette_row + 0.5) / 8.0));
 if (index < 0.5 || encoded.a < 0.5) { COLOR.a = 0.0; }
}
