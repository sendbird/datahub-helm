# Mirroring DataHub Actions

### descriptions of files

* Dockerfile
  - It builds the docker image.
    It copies all required files such as *.py and *.yml, then run the start_datahub_actions.sh script. 
* start_datahub_actions.sh
  - This script file executes mirroring actions with configured yaml files.
* logrotate.conf
  - logrotate configuration file. logrotate is for preventing too high disk usage by log files.
* gql_get_sb_regions.py
  - It is for getting sb_regions list from DataHub metadata.
* mirror_action.py
  - It is the core of this custom-datahub-actions. This inherited Action class specifies how to act on incoming events.
  - watching aspects
    * editableDatasetProperties (table level description)
    * editableSchemaMetadata (column level description/tags)
    * ownership (owners)
    * globalTags (table level tags) 
  
### action.config

* gql_query
  - It is for getting all available sendbird_regions.
  - For example, to get all sendbird_regions in sb-dw-mesg-prod, we can query 'sb-dw-mesg-{env}.log_access.*'.
    'log_access' dataset has tables of which name is sendbird_region.
* platform
  - bigquery / mysql / elasticsearch / ...
* source_sb_region
  - which sb_region is source? If source region is ap1, then when ap1 metadata is changed it is being mirrored to other sendbird_regions except source.
* source_sb_region_stg
  - staging does not have a region name ap1 but have something like staging. 
* table_name_template
  - regular expression form.
  - we consider only tables that are searched with this regular expression.
  