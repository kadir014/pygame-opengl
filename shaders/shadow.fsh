#version 330


in vec2 v_texture;
in vec3 v_normal;
in vec3 FragPos;
in vec4 lightspace;

out vec4 out_color;

uniform vec3 viewpos;
uniform vec3 lightpos;
uniform vec3 color;
uniform float ambient_intensity;
uniform float diffuse_intensity;
uniform float specular_intensity;
uniform float specular_power;

uniform sampler2D s_texture;
uniform samplerCube skybox;
uniform sampler2D shadowMap;


float ShadowCalculation(vec4 ls)
{
    // perform perspective divide
    vec3 projCoords = ls.xyz / ls.w;
    projCoords = projCoords * 0.5 + 0.5;
    float closestDepth = texture(shadowMap, projCoords.xy).r;
    float currentDepth = ls.z;  
    float shadow = currentDepth > closestDepth  ? 1.0 : 0.0;  

    return shadow;
}


void main() {
    // Ambient
    vec3 ambient = ambient_intensity * color;
    
    // Diffuse
    vec3 norm = normalize(v_normal);
    vec3 lightDir = normalize(lightpos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * color * diffuse_intensity;
    
    // Specular
    vec3 viewDir = normalize(viewpos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), specular_power);
    vec3 specular = specular_intensity * spec * color;

    vec3 I = normalize(FragPos - viewpos);
    vec3 R = reflect(I, normalize(v_normal));
    vec4 refl = vec4(texture(skybox, R).rgb, 1.0);

    // float visibility = 1.0;
    // if ( texture( shadowMap, FragPos.xy ).z  <  FragPos.z){
    //     visibility = 0.2;
    // }

    // float depth = 1.0;
    // vec3 lightcoords = Shadowa.xyz / Shadowa.w;
    //     lightcoords = (lightcoords + 1.0) / 2.0;

    //     depth = texture(shadowMap, lightcoords);

    //float depth = texture(shadowMap, FragPos);
    
    float shadow = ShadowCalculation(lightspace);       
    
    vec3 result = texture(s_texture, v_texture).xyz * (ambient + diffuse + specular) * shadow;
    out_color = vec4(result, 1.0) * refl;

    //out_color = vec4(vec3(depth), 1.0);
}