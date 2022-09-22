from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext
import json
import logging
from datahub.emitter.mcp import MetadataChangeProposalWrapper
# read-modify-write requires access to the DataHubGraph (RestEmitter is not enough)
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph
# Imports for metadata model classes
from datahub.metadata.schema_classes import (
    ChangeTypeClass,
    GlobalTagsClass,
    TagAssociationClass,
    OwnerClass,
    OwnershipClass,
    EditableDatasetPropertiesClass,
    EditableSchemaMetadataClass,
    EditableSchemaFieldInfoClass,
    AuditStampClass,
)
import re
import os

from gql_get_sb_regions import get_sb_regions

ENV = os.getenv('ENV', 'stg')
GMS_ENDPOINT = os.getenv('GMS_ENDPOINT', '')
GMS_TOKEN = ''

logger = logging.getLogger(__name__)

graph = DataHubGraph(
    DatahubClientConfig(
        server=GMS_ENDPOINT,
        token=GMS_TOKEN,
    ))


def replaceUrnFromSourceToTarget(urn: str,
                                 target_sb_region: str,
                                 sb_region_index_from_name: int,
                                 is_elasticsearch: bool = False) -> str:
  urn_splitted = urn.split(',')
  table_name = urn_splitted[1]
  splitted = table_name.split('.')
  source_sb_region = splitted[sb_region_index_from_name]
  splitted[sb_region_index_from_name] = target_sb_region
  processed_table_name = '.'.join(splitted)
  if is_elasticsearch:
    processed_table_name = processed_table_name.replace(
        source_sb_region, target_sb_region)
  urn_splitted[1] = processed_table_name
  return ','.join(urn_splitted)


class MirrorAction(Action):
  @classmethod
  def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
    logger.info(ctx)
    logger.info(config_dict)
    gql_query = config_dict['gql_query']
    gql_query = gql_query.replace('{env}', ENV.lower())
    table_name_template = config_dict['table_name_template']
    platform = config_dict['platform']
    # For BigQuery, name is like `sb-dw-mesg-prod.log_access.ap1`. When this string is splitted by '.', the index that points to sb_region is -1.
    # For others, name is like `ap1.soda.main_aametrics`. Thus, sb_region_index_from_name is 0.
    sb_region_index_from_name = 0 if platform != 'bigquery' else -1
    source_sb_region = config_dict[
        'source_sb_region'] if ENV == 'prod' else config_dict[
            'source_sb_region_stg']

    cls.target_sb_regions = get_sb_regions(
        gms_endpoint=GMS_ENDPOINT,
        token=GMS_TOKEN,
        gql_query=gql_query,
        platform=platform,
        sb_region_index_from_name=sb_region_index_from_name,
    )
    cls.platform = platform
    cls.table_name_template = table_name_template
    cls.sb_region_index_from_name = sb_region_index_from_name
    cls.source_sb_region = source_sb_region

    return cls(ctx)

  def __init__(self, ctx: PipelineContext):
    self.ctx = ctx
    logger.info(self.target_sb_regions)

  def metadata_change_editableDatasetProperties_for(self, targetEntityUrn: str,
                                                    json_aspect_val: dict):
    # table level description
    mcpw: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType='dataset',
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=targetEntityUrn,
        aspectName='editableDatasetProperties',
        aspect=EditableDatasetPropertiesClass(
            description=json_aspect_val['description'],
            created=AuditStampClass(time=json_aspect_val['created']['time'],
                                    actor=json_aspect_val['created']['actor'])
            if json_aspect_val.get('created') is not None else None,
            lastModified=AuditStampClass(
                time=json_aspect_val['lastModified']['time'],
                actor=json_aspect_val['lastModified']['actor'])
            if json_aspect_val.get('lastModified') is not None else None,
        ),
    )
    logger.info(mcpw)
    graph.emit(mcpw)

  def metadata_change_editableSchemaMetadata_for(self, targetEntityUrn: str,
                                                 json_aspect_val: dict):
    # column level description/tags
    editableSchemaFieldInfoClassList = []
    for each in json_aspect_val['editableSchemaFieldInfo']:
      fieldPath = each.get('fieldPath')
      description = each.get('description')
      globalTags = each.get('globalTags') or {}
      tags = globalTags.get('tags') or []
      tagAssociationClassList = []
      for tag in tags:
        tagAssociationClassList.append(TagAssociationClass(tag=tag.get('tag')))
      editableSchemaFieldInfoClassList.append(
          EditableSchemaFieldInfoClass(
              fieldPath=fieldPath,
              description=description,
              globalTags=GlobalTagsClass(tags=tagAssociationClassList)
              if tagAssociationClassList else None,
          ))
    mcpw: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType='dataset',
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=targetEntityUrn,
        aspectName='editableSchemaMetadata',
        aspect=EditableSchemaMetadataClass(
            editableSchemaFieldInfo=editableSchemaFieldInfoClassList, ),
    )
    logger.info(mcpw)
    graph.emit(mcpw)

  def metadata_change_ownership_for(self, targetEntityUrn: str,
                                    json_aspect_val: dict):
    # table level ownership
    ownerClassList = []
    for each in json_aspect_val['owners']:
      owner = each.get('owner')
      htype = each.get('type')
      source = each.get('source')
      ownerClassList.append(
          OwnerClass(
              owner=owner,
              type=htype,
              source=source,
          ))
    mcpw: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType='dataset',
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=targetEntityUrn,
        aspectName='ownership',
        aspect=OwnershipClass(
            owners=ownerClassList,
            lastModified=AuditStampClass(
                time=json_aspect_val['lastModified']['time'],
                actor=json_aspect_val['lastModified']['actor'])
            if json_aspect_val.get('lastModified') is not None else None,
        ),
    )
    logger.info(mcpw)
    graph.emit(mcpw)

  def metadata_change_globalTags_for(self, targetEntityUrn: str,
                                     json_aspect_val: dict):
    # table level tags
    tagAssociationClassList = []
    for each in json_aspect_val['tags']:
      tag = each.get('tag')
      if tag.split(':')[-2] == 'sendbird_region':
        continue
      tagAssociationClassList.append(TagAssociationClass(tag=tag, ))
    mcpw: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
        entityType='dataset',
        changeType=ChangeTypeClass.UPSERT,
        entityUrn=targetEntityUrn,
        aspectName='globalTags',
        aspect=GlobalTagsClass(tags=tagAssociationClassList, ),
    )
    logger.info(mcpw)
    graph.emit(mcpw)

  def act(self, event: EventEnvelope) -> None:
    if event.event_type != 'MetadataChangeLogEvent_v1':
      return
    logger.info('-' * 10 + ' event')
    logger.info(event)
    logger.info('-' * 10 + ' event')
    ev = event.event
    aspect = getattr(ev, 'aspect', None)
    if not aspect:
      return
    aspect_val = aspect.value
    json_aspect_val = json.loads(aspect_val)
    logger.info(f'json_aspect_val: {json_aspect_val}')

    table_name = self.table_name_template.replace('{env}',
                                                  ENV.lower()).replace(
                                                      '{sendbird_region}',
                                                      self.source_sb_region)
    built_dataset_urn_regexp = f'urn:li:dataset:\(urn:li:dataPlatform:{self.platform},{table_name},{ENV.upper()}\)'

    if not re.search(built_dataset_urn_regexp, ev.entityUrn):
      return
    for target_sb_region in self.target_sb_regions:
      if target_sb_region in (self.source_sb_region, ):
        continue
      targetEntityUrn = replaceUrnFromSourceToTarget(
          ev.entityUrn,
          target_sb_region,
          self.sb_region_index_from_name,
          is_elasticsearch=True if self.platform == 'elasticsearch' else False)
      logger.info(f'targetEntityUrn: {targetEntityUrn}')
      if ev.aspectName == 'editableDatasetProperties':
        self.metadata_change_editableDatasetProperties_for(
            targetEntityUrn, json_aspect_val)

      elif ev.aspectName == 'editableSchemaMetadata':
        self.metadata_change_editableSchemaMetadata_for(
            targetEntityUrn, json_aspect_val)

      elif ev.aspectName == 'ownership':
        self.metadata_change_ownership_for(targetEntityUrn, json_aspect_val)

      elif ev.aspectName == 'globalTags':
        self.metadata_change_globalTags_for(targetEntityUrn, json_aspect_val)

  def close(self) -> None:
    pass
