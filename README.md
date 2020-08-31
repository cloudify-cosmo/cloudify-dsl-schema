# Cloudify DSL Schema

The project contains JSON Schema for Cloudify Blueprints.

## What you can do?
### Autocomplete
Similar to any programing language you can press `CTRL+SPACE` and it will suggest what are the available options.

### Suggest properties based on type
In the node templates when you specify `type` the JSON schema will suggest properties and interfaces that are available for that specific type.

### Detect Missing Mandatory Fields
If a mandatory field is expected and it's missing you'll get a notification. 

### Detect unknown property
Some of the objects are sealed to certain properties. If an unkown property is introduced it will show an error message. It's good in cases when an attribute is misspelled.

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

## Supported Plugin
- [cloudify-docker-plugin](https://github.com/cloudify-cosmo/cloudify-docker-plugin)
- [cloudify-kubernetes-plugin](https://github.com/cloudify-cosmo/cloudify-kubernetes-plugin)
- [cloudify-ansible-plugin](https://github.com/cloudify-cosmo/cloudify-ansible-plugin)
- [cloudify-terraform-plugin](https://github.com/cloudify-cosmo/cloudify-terraform-plugin)
- [cloudifu-aws-plugin (prtially)](https://github.com/cloudify-cosmo/cloudify-aws-plugin)
- [cloudify-openstack-plugin](https://github.com/cloudify-cosmo/cloudify-openstack-plugin)

## Comming Soon
- [cloudify-utilities-plugin](https://github.com/cloudify-incubator/cloudify-utilities-plugin)
- [cloudify-aws-plugin](https://github.com/cloudify-cosmo/cloudify-aws-plugin)
- [cloudify-azure-plugin](https://github.com/cloudify-cosmo/cloudify-azure-plugin)
- [cloudify-gcp-plugin](https://github.com/cloudify-cosmo/cloudify-gcp-plugin)
- [cloudify-vsphere-plugin](https://github.com/cloudify-cosmo/cloudify-vsphere-plugin)
- [tosca-vcloud-plugin](https://github.com/cloudify-cosmo/tosca-vcloud-plugin)
 
## Adding support for your plugin