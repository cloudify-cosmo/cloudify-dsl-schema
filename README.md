# Cloudify DSL Schema

The project contains JSON Schema for Cloudify Blueprints.

## What you can do?
### Autocomplete
Similar to any programing language you can press `CTRL+SPACE` and it will suggest what are the available options.

### Property Type Validation
Each property is assigned to a specific type. The type can be `integer`, `string`, `boolean`, `object`, `array`. If the value is not of the right type the IDE will notify you about it.

![Wrong Property Format](/images/wrong_property_type.png)
> NOTE: for properties that are populated during a runtime with intrinsic functions from `input`, `secret`, `property` or `attribute` the error will be thrown during the runtime.
 
### Suggest properties based on type
In the node templates when you specify `type` the JSON schema will suggest properties and interfaces that are available for that specific type.

As you can see in the images bellow the available properties for type `cloudify.rest.request` are different from `cloudify.nodes.ftp`

Cloudify Rest Request 

![Cloudify Rest Request](/images/properties_rest_request.png)

Cloudify FTP

![Cloudify FTP](/images/properties_ftp.png)

### Detect Missing Required Properties
If a mandatory field is expected and it's missing you'll get a notification. 

![Missing Mandatory Property](/images/property_missing.png)

### Property Description
For most of the properties a description is available. The description can assist you to understand what is the best way to use it.

![File Mode Description](/images/property_description.png)

### Detect not allowed property
Some of the objects are sealed to certain properties. If an unknown property is introduced it will show an error message. It's good in cases when an attribute is misspelled.

![Not Allowed Property](/images/property_not_allowed.png)

### IDE Integration

The JSON Schema is uploaded to [SchemaStore](http://www.schemastore.org/json/).

The integration provides Cloudify Json schema to be auto available in the following IDEs: 
- IntelliJ IDEA
- PhpStorm
- PyCharm
- Rider
- RubyMine
- Visual Studio 2013+
- Visual Studio Code
- Visual Studio for Mac
- WebStorm
- JSONBuddy

All you need is to save your file that matches the patter `*.cfy.yaml`

## Supported Plugins
- [x] [cloudify-docker-plugin](https://github.com/cloudify-cosmo/cloudify-docker-plugin)
- [x] [cloudify-kubernetes-plugin](https://github.com/cloudify-cosmo/cloudify-kubernetes-plugin)
- [x] [cloudify-ansible-plugin](https://github.com/cloudify-cosmo/cloudify-ansible-plugin)
- [x] [cloudify-terraform-plugin](https://github.com/cloudify-cosmo/cloudify-terraform-plugin)
- [x] [cloudifu-aws-plugin (prtially)](https://github.com/cloudify-cosmo/cloudify-aws-plugin)
- [x] [cloudify-openstack-plugin](https://github.com/cloudify-cosmo/cloudify-openstack-plugin)
- [x] [cloudify-utilities-plugin](https://github.com/cloudify-incubator/cloudify-utilities-plugin)
- [x] [cloudify-azure-plugin](https://github.com/cloudify-cosmo/cloudify-azure-plugin)
- [ ] [cloudify-gcp-plugin](https://github.com/cloudify-cosmo/cloudify-gcp-plugin)
- [ ] [cloudify-vsphere-plugin](https://github.com/cloudify-cosmo/cloudify-vsphere-plugin)
- [ ] [tosca-vcloud-plugin](https://github.com/cloudify-cosmo/tosca-vcloud-plugin)
 
## Adding your plugin's node type support

The section explain how to add support for your plugin node types to node template.

It will walk you though on how to add a condition on a node template type property so the properties and interfaces will be corolated to your node type.

Open [cloudify_dsl.schema.json](/cloudify_dsl.schema.json) file.

Add properties and interfaces definitions of your object.
 
For example if your node type is `cloudify.kubernetes.resources.BlueprintDefinedResource`

Create 2 definitions one for properties `nodeTypeKubernetesResourcesBlueprintDefinedResourceProperties` and the second one for interfaces `nodeTypeKubernetesResourcesBlueprintDefinedResourceInterfaces`
 
Add condition on type property for node template in the list `/properties/definitions/nodeTemplate/allOff`

for the example above it will look like

``` javascript
{
    "if": { 
      "properties": { 
        "type": { 
          "const": "cloudify.kubernetes.resources.BlueprintDefinedResource" 
        }
      }
    },
    "then": { 
      "properties": {
        "properties": { 
          "$ref": "#/definitions/nodeTypeKubernetesResourcesBlueprintDefinedResourceProperties"
        },
        "interfaces": { 
          "$ref": "#/definitions/nodeTypeKubernetesResourcesBlueprintDefinedResourceInterfaces"
        }
      }
    }
}
```

 
For how to write JSON Schema please follow the link [json-schema.org](https://json-schema.org)

to add support for your plugin node type
