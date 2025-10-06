from __future__ import annotations

from typing import Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator
from datetime import datetime
from typing_extensions import Literal

class MyTrapperBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def pprint(self):
        from pprint import pprint

        pprint(self.dict())

class Pagination(BaseModel):
    page: int
    page_size: int
    pages: int
    count: int

#
# Trapper Locations
#

class TrapperLocation(MyTrapperBase):
    locationID: str
    longitude: float
    latitude: float
    country: Optional[str] = None
    timezone: str
    ignoreDST: bool = Field(default=False)
    habitat: Optional[str] = None
    comments: Optional[str] = None
    id: str = Field(..., alias="_id")
    researchProject: Optional[str] = None

class TrapperLocationList(MyTrapperBase):
    pagination: Pagination
    results: List[TrapperLocation]

#
# Deployments
#

class TrapperDeployment(MyTrapperBase):
    deploymentID: str
    locationID: str
    locationName: str
    latitude: float
    longitude: float
    coordinateUncertainty: Optional[float] = None
    deploymentStart: datetime
    deploymentEnd: Optional[datetime] = None
    setupBy: Optional[str] = None
    cameraID: Optional[str] = None
    cameraModel: Optional[str] = None
    cameraDelay: Optional[str] = None
    cameraHeight: Optional[str] = None
    cameraDepth: Optional[str] = None
    cameraTilt: Optional[str] = None
    cameraHeading: Optional[str] = None
    detectionDistance: Optional[str] = None
    timestampIssues: Optional[bool] = None
    baitUse: Optional[bool] = None
    featureType: Optional[str] = None
    habitat: Optional[str] = None
    deploymentGroups: Optional[str] = None
    deploymentTags: Optional[str] = None
    deploymentComments: Optional[str] = None
    id: str = Field(..., alias="_id")
    timezone: Optional[str] = None

class TrapperDeploymentList(MyTrapperBase):
    pagination: Pagination
    results: List[TrapperDeployment]

#
# Classification Projects
#

class TrapperClassificationProjectRole(BaseModel):
    user: str
    profile: str
    roles: List[str]

class TrapperClassificationProject(BaseModel):
    pk: int
    name: str
    owner: str
    owner_profile: str
    classificator: int
    research_project: str
    status: str
    is_active: bool
    project_roles: List[TrapperClassificationProjectRole]
    classificator_removed: bool
    update_data: str
    detail_data: str
    delete_data: str

class TrapperClassificationProjectList(MyTrapperBase):
    pagination: Pagination
    results: List[TrapperClassificationProject]

#
# Research Projects
#

class TrapperResearchProjectRole(BaseModel):
    user: str
    username: str
    profile: str
    roles: List[str]

class TrapperResearchProject(BaseModel):
    pk: int
    name: str
    owner: str
    owner_profile: str
    acronym: str
    keywords: List[str]
    date_created: datetime
    project_roles: List[TrapperResearchProjectRole]
    update_data: Optional[str] = None
    detail_data: Optional[str] = None
    delete_data: Optional[str] = None
    status: Optional[bool] = None

class TrapperResearchProjectList(BaseModel):
    pagination: Pagination
    results: List[TrapperResearchProject]

#
# Collections
#

class TrapperCollectionRole(BaseModel):
    user: str
    username: str
    profile: str
    roles: List[str]

# Obtenido de consultar por CP
class TrapperCollectionCP(BaseModel):
    pk: int
    collection_pk: int
    name: str
    status: str
    is_active: bool
    detail_data: str
    classify_data: str
    approved_count: int
    classified_count: int
    total_count: int

# Obtenido de consultar por RP
class TrapperCollectionRP(BaseModel):
    pk: int
    collection_pk: int
    name: str
    owner: Optional[str] = None
    owner_profile: Optional[str] = None
    status: Optional[str] = None
    date_created: Optional[datetime] = None
    description: Optional[str] = None
    detail_data: Optional[str] = None
    delete_data: Optional[str] = None

class TrapperCollection(BaseModel):
    pk: int
    name: str
    owner: Optional[str] = None
    owner_profile: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    update_data: Optional[str] = None
    detail_data: Optional[str] = None
    delete_data: Optional[str] = None

class TrapperCollectionList(BaseModel):
    pagination: Pagination
    results: List[Union[TrapperCollection, TrapperCollectionRP, TrapperCollectionCP]]

# Resources
#

class TrapperResourceCollection(BaseModel):
    pk: int
    name: str
    owner: Optional[str] = None
    owner_profile: Optional[str] = None
    resource_type: str
    date_recorded: datetime
    observation_type: Optional[List[str]] = None
    species: Optional[List[str]] = None
    tags: List[str]
    url: str
    url_original: str
    mime: str
    thumbnail_url: str
    update_data: str
    detail_data: str
    delete_data: str
    date_recorded_correct: bool

class TrapperResourceLocation(BaseModel):
    pk: int
    name: str
    resource_type: str
    deployment: str
    date_recorded: datetime
    tags: List[str]
    thumbnail_url: str
    detail_data: str

class TrapperResource(BaseModel):
    pk: int
    name: str
    owner: Optional[str] = None
    owner_profile: Optional[str] = None
    resource_type: str
    date_recorded: datetime
    deployment: Optional[str] = None
    observation_type: Optional[List[str]] = None
    species: Optional[List[str]] = None
    tags: List[str]
    url: Optional[str] = None
    url_original: str = None
    mime: Optional[str] = None
    thumbnail_url: str
    update_data: Optional[str] = None
    detail_data: Optional[str] = None
    delete_data: Optional[str] = None
    date_recorded_correct: Optional[bool] = None

class TrapperResourceList(BaseModel):
    pagination: Pagination
    results: List[TrapperResource]
    results: List[Union[TrapperResourceCollection, TrapperResourceLocation]]

###
### Media
###

class TrapperMedia(BaseModel):
    mediaID: int
    deploymentID: str
    captureMethod: str
    timestamp: datetime
    filePath: HttpUrl
    filePublic: bool
    fileName: str
    fileMediatype: str
    exifData: Optional[str] = None
    favorite: bool
    mediaComments: Optional[str] = None
    id: str = Field(..., alias="_id")

class TrapperMediaList(BaseModel):
    pagination: Pagination
    results: List[TrapperMedia]

###
### Observations
###

class TrapperObservation(BaseModel):
    observationID: int
    deploymentID: str
    mediaID: int
    eventID: str
    eventStart: datetime
    eventEnd: datetime
    observationLevel: str
    observationType: str
    cameraSetupType: Optional[str] = None
    scientificName: Optional[str] = None
    count: Optional[int] = None
    countNew: Optional[int] = None
    lifeStage: Optional[str] = None
    sex: Optional[str] = None
    behavior: Optional[str] = None
    individualID: Optional[str] = None
    bboxes: Optional[List[float]] = None  # podría ser lista de coordenadas si contiene cajas
    classificationMethod: Optional[str] = None
    classifiedBy: Optional[str] = None
    classificationTimestamp: Optional[datetime] = None
    classificationProbability: Optional[float] = None
    observationTags: Optional[List[str]] = None
    observationComments: Optional[str] = None
    id: str = Field(..., alias="_id")

    @field_validator("count", "countNew", "bboxes", "classificationTimestamp","classificationProbability", "observationTags", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class TrapperObservationList(BaseModel):
    pagination: Pagination
    results: List[TrapperObservation]