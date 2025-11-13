from __future__ import annotations

from typing import Optional, List, Union, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator, model_validator, AnyUrl
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
# GeoJSON Feature
#

class Coordinates(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def from_string(cls, value: str):
        """Convierte '1.0, 1.0' o '1.0 1.0' en Coordinates"""
        try:
            parts = [p.strip() for p in value.replace(" ", ",").split(",") if p.strip()]
            if len(parts) != 2:
                raise ValueError
            lat, lon = map(float, parts)
            return cls(latitude=lat, longitude=lon)
        except Exception:
            raise ValueError(f"Formato de coordenadas no válido: {value}")


class Geometry(BaseModel):
    type: Literal["Point"]  # puedes ampliar con otros tipos si lo necesitas
    coordinates: List[float]  # [lon, lat] o [x, y]


class Properties(BaseModel):
    pk: int
    location_id: str
    name: Optional[str] = None


class Feature(BaseModel):
    type: Literal["Feature"]
    geometry: Geometry
    properties: Properties


# ##############################################################################
# Trapper Locations
# ##############################################################################

# LocationViewSet

class TrapperLocation(BaseModel):
    pk : int
    name: Optional[str] = None
    date_created: datetime
    description: Optional[str] = None
    location_id: str
    is_public: bool
    coordinates: Coordinates
    owner: str
    # TODO: AnyRL
    owner_profile: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    research_project: Optional[str] = None
    timezone: Optional[str] = None
    update_data: Optional[str] = None
    delete_data: Optional[str] = None

    @field_validator("coordinates", mode="before")
    def parse_coordinates(cls, value):
        """Acepta tanto una cadena 'lat, lon' como un diccionario o instancia Coordinates"""
        if isinstance(value, str):
            return Coordinates.from_string(value)
        elif isinstance(value, dict):
            return Coordinates(**value)
        elif isinstance(value, Coordinates):
            return value
        raise TypeError(f"Tipo no válido para coordinates: {type(value)}")

# LocationTableView

#class LocationTable(BaseModel):
#    locationID: Optional[str] = None
#    longitude: Optional[float] = None
#    latitude: Optional[float] = None
#    country_timezone: Optional[str] = None
#    ignoreDST: Optional[bool] = None
#    habitat: Optional[str] = None
#    comments: Optional[str] = None
#    id: Optional[str] = Field(None, alias="_id")
#    researchProject: Optional[str] = None


# LocationGeoViewSet

class TrapperLocationGeo(Feature):
    pass

#class TrapperLocation(MyTrapperBase):
#    locationID: str
#    longitude: float
#    latitude: float
#    country: Optional[str] = None
#    timezone: str
#    ignoreDST: bool = Field(default=False)
#    habitat: Optional[str] = None
#    comments: Optional[str] = None
#    id: str = Field(..., alias="_id")
#    researchProject: Optional[str] = None

class TrapperLocationList(MyTrapperBase):
    pagination: Pagination
    results: List[TrapperLocation]

# ##############################################################################
# Deployments
# ##############################################################################

class TrapperDeployment2(MyTrapperBase):
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

class TrapperDeployment(MyTrapperBase):
    pk: int
    deployment_code: str
    deployment_id: str
    location: int
    location_id: str
    start_date: datetime
    end_date: datetime
    owner: str
    owner_profile: Optional[str]  # Es una URL relativa
    research_project: Optional[str] = None
    tags: List[str]
    correct_setup: bool
    correct_tstamp: bool
    detail_data: Optional[str]  # URL relativa
    update_data: Optional[str]  # URL relativa
    delete_data: Optional[str]  # URL relativa

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

#ClassificationProjectViewSet
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
"""
class TrapperResourceCollection(BaseModel):
    pk: int
    name: str
    owner: str
    owner_profile: str
    resource_type: str
    date_recorded: datetime
    observation_type: List[str]
    species: List[str]
    tags: List[str]
    url: str
    url_original: str
    mime: str
    preview_url : str
    thumbnail_url: str
    update_data: str = None
    detail_data: str
    delete_data: str = None
    date_recorded_correct: bool
"""

class TrapperResourceLocation(BaseModel):
    pk: int
    resource_type: str
    deployment: Optional[str] = None
    date_recorded: datetime
    tags: List[str]
    preview_url : str
    thumbnail_url: str
    detail_data: str

class TrapperResource(BaseModel):
    pk: int
    name: str
    owner: str
    owner_profile: str
    resource_type: str
    date_recorded: datetime
    observation_type: List[str]
    species: List[str]
    tags: List[str]
    url: str
    url_original: str
    mime: str
    preview_url : str
    thumbnail_url: str
    update_data: str
    detail_data: str
    delete_data: str
    date_recorded_correct: bool

class TrapperResourceList(BaseModel):
    pagination: Pagination
    results: List[Union[TrapperResource, TrapperResourceLocation]]

#######################################################################################################################
### Media
#######################################################################################################################

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
    # id: str = Field(..., alias="_id")

class TrapperMediaList(BaseModel):
    pagination: Pagination
    results: List[TrapperMedia]

### ####################################################################################################################
### Observations
### ####################################################################################################################


class TrapperResourceC(BaseModel):
    pk: int
    name: str
    resource_type: str = Field(..., description="Tipo de recurso, p.ej. 'I' para imagen")
    thumbnail_url: Optional[str] = Field(None, description="URL del thumbnail")
    url: Optional[str] = Field(None, description="URL del recurso completo")
    mime: Optional[str] = Field(None, description="Tipo MIME del recurso")
    date_recorded: Optional[datetime] = Field(None, description="Fecha de captura del recurso")
    deployment: Optional[int] = Field(None, description="ID numérico del despliegue")
    deployment_id: Optional[str] = Field(None, description="Identificador textual del despliegue")

class DynamicAttr(BaseModel):
    observation_type: Optional[str] = Field(default=None)
    species: Optional[str] = Field(default=None)
    count: Optional[str] = Field(default=None)
    classification_confidence: Optional[str] = Field(default=None)

    @model_validator(mode="before")
    @classmethod
    def unwrap_value_dicts(cls, values: Any) -> Any:
        """
        Si el modelo recibe un diccionario donde los campos son del tipo {'value': '...'},
        convierte todos esos valores a cadenas simples antes de la validación.
        """
        if isinstance(values, dict):
            new_values = {}
            for k, v in values.items():
                if isinstance(v, dict) and "value" in v:
                    new_values[k] = v["value"]
                else:
                    new_values[k] = v
            return new_values
        return values

# ClassificationViewSet
class TrapperClassification(BaseModel):
    pk: int
    resource: TrapperResourceC
    collection: int
    updated_at: datetime
    is_setup: bool
    static_attrs: Dict[str, Any] = Field(default_factory=dict)
    dynamic_attrs: List[DynamicAttr] = Field(default_factory=list)
    status: bool
    status_ai: bool
    classified: bool
    classified_ai: bool
    classification_project: str
    detail_data: Optional[str]
    delete_data: Optional[str]
    classify_data: Optional[str] = None
    update_data: Optional[str] = None
    bboxes: Optional[bool] = None

# AIClassificationViewSet
class TrapperAIClassification(BaseModel):
    pk: int
    owner: str
    owner_profile: Optional[str]
    classification: int
    resource: TrapperResourceC
    collection: int
    updated_at: datetime
    approved: bool
    created_at: datetime
    static_attrs: Dict[str, str]
    dynamic_attrs: List[DynamicAttr]
    detail_data: Optional[str]
    delete_data: Optional[str]
    ai_provider: Optional[str]

#UserClassificationViewSet
class TrapperUserClassification(BaseModel):
    pk: int
    owner: str
    owner_profile: Optional[str]
    classification: int
    resource: TrapperResourceC
    collection: int
    updated_at: datetime
    approved: bool
    created_at: datetime
    static_attrs: Dict[str, str]
    dynamic_attrs: List[DynamicAttr]
    detail_data: Optional[str]
    delete_data: Optional[str]

#ClassificationResultsView.
class TrapperObservationResults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observationID: int
    deploymentID: str
    mediaID: int
    eventID: str
    eventStart: datetime
    eventEnd: datetime
    observationLevel: str
    observationType: str
    cameraSetupType: Optional[str]
    scientificName: Optional[str]
    count: Optional[int]
    lifeStage: Optional[str]
    sex: Optional[str]
    behavior: Optional[str]
    individualID: Optional[str]
    individualPositionRadius: Optional[str]
    individualPositionAngle: Optional[str]
    individualSpeed: Optional[str]
    classificationMethod: Optional[str]   # No aparece en AI y User
    classifiedBy: Optional[str]
    classificationTimestamp: Optional[datetime]
    classificationProbability: Optional[float]
    observationTags: Optional[str]
    observationComments: Optional[str]

    @field_validator("*", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None

        return v

    @field_validator("classificationProbability", "mediaID", "count", "observationID", mode="before")
    def convert_to_float_or_int(cls, v):
        if v in (None, ""):
            return None
        try:
            s = str(v)
            if "." in s:
                return float(s)
            return int(s)
        except (ValueError, TypeError):
            return None

    @field_validator("classificationTimestamp", mode="before")
    def parse_datetime(cls, v):
        if not v:
            return None
        from datetime import datetime
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            return None

class TrapperObservationResultsTrapper(TrapperObservationResults):
    countNew: Optional[int]
    englishName: Optional[str]
    bboxes: Optional[List[List[float]]]
    id: Optional[str] = Field(..., alias="_id", description="Internal database identifier")


    @field_validator("bboxes", mode="before")
    def parse_bboxes(cls, v):
        import json, ast
        if v in (None, "", []):  # vacío → lo dejo igual
            return v
        if isinstance(v, str):
            try:
                # primero intento JSON normal
                return json.loads(v)
            except Exception:
                try:
                    # si no es JSON válido, intento evaluarlo como lista de Python
                    return ast.literal_eval(v)
                except Exception:
                    raise ValueError(f"Invalid bboxes format: {v}")

        return v

class TrapperObservationResultsCTDP(TrapperObservationResults):
    bboxX: Optional[float] = None
    bboxY: Optional[List[float]] = None
    bboxWidth: Optional[float] = None
    bboxHeight: Optional[float] = None

    @field_validator("bboxX", "bboxY", "bboxWidth", "bboxHeight", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

        return v

class TrapperAIObservationResults(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
    lifeStage: Optional[str] = None
    sex: Optional[str] = None
    behavior: Optional[str] = None
    individualID: Optional[str] = None
    individualPositionRadius: Optional[str] = None
    individualPositionAngle: Optional[str] = None
    individualSpeed: Optional[str] = None
    classifiedBy: Optional[str] = None
    classificationTimestamp: Optional[datetime] = None
    classificationProbability: Optional[float] = None

    @field_validator("count", "classificationTimestamp","classificationProbability", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

        return v

class TrapperAIObservationResultsTrapper(TrapperAIObservationResults):
    observationID: Optional[str]
    countNew: Optional[int] = None
    englishName: Optional[str] = None
    bboxes: Optional[List[List[float]]] = None
    id: Optional[str] = Field(None, alias="_id", description="Internal database identifier")

    @field_validator("countNew", "bboxes", mode="before")
    def empty_string_to_none_2(cls, v):
        if v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

        return v

    @field_validator("bboxes", mode="before")
    def parse_bboxes(cls, v):
        import json, ast
        if v in (None, "", []):  # vacío → lo dejo igual
            return v
        if isinstance(v, str):
            try:
                # primero intento JSON normal
                return json.loads(v)
            except Exception:
                try:
                    # si no es JSON válido, intento evaluarlo como lista de Python
                    return ast.literal_eval(v)
                except Exception:
                    raise ValueError(f"Invalid bboxes format: {v}")

        return v

class TrapperAIObservationResultsCTDP(TrapperAIObservationResults):
    bboxesX: Optional[float] = None
    bboxesY: Optional[List[float]] = None
    bboxWidth: Optional[float] = None
    bboxHeight: Optional[float] = None

    @field_validator("bboxesY", "bboxesX", "bboxWidth", "bboxHeight", mode="before")
    def empty_string_to_none_2(cls, v):
        if v == "":
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

        return v

class ClassificationResultsAgg(BaseModel):
    deploymentID :str
    locationID : Optional[str] = None
    locationName : Optional[str] = None
    latitude : float
    longitude : float
    coordinateUncertainty : int
    deploymentStart : datetime
    deploymentEnd: datetime
    setupBy : Optional[str] = None
    cameraID : Optional[str] = None
    cameraModel : Optional[str] = None
    cameraDelay : Optional[float] = None
    cameraHeight : Optional[float] = None
    cameraDepth : Optional[float] = None
    cameraTilt : Optional[float] = None
    cameraHeading : Optional[float] = None
    detectionDistance : Optional[float] = None
    timestampIssues : bool
    baitUse : bool
    featureType : Optional[str] = None
    habitat : Optional[str] = None
    deploymentGroups: Optional[str] = None
    deploymentTags : Optional[str] = None
    deploymentComments : Optional[str] = None
    days : int
    observationType : Optional[str] = None
    scientificName : Optional[str] = None
    count : Optional[int] = None
    trapRate : Optional[float] = None

    @field_validator("*", mode="before")
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class TrapperClassificationList(BaseModel):
    pagination: Pagination
    #results: List[Union[TrapperClassification, TrapperAIClassification, TrapperUserClassification]]
    results: List[Union[TrapperClassification
                        , TrapperAIClassification
                        , TrapperUserClassification
                        , TrapperObservationResults
                        , TrapperAIObservationResults
    #                    , ClassificationResultsAgg
    ]]

class TrapperClassificationResultsList(BaseModel):
    pagination: Pagination
    #results: List[Union[TrapperClassification, TrapperAIClassification, TrapperUserClassification]]
    results: List[Union[
                          TrapperObservationResultsCTDP
                        , TrapperObservationResultsTrapper
                        , TrapperAIObservationResultsTrapper
                        , TrapperAIObservationResultsCTDP
        #                   , ClassificationResultsAgg
    ]]


class TrapperObservationList(BaseModel):
    pagination: Pagination
    results: List[TrapperObservation]

#
# Classificator
#

# ClassificatorViewSet
class TrapperClassificator(BaseModel):
    pk: int
    name: str
    owner: str
    owner_profile: str
    updated_date: str  # ISO 8601 string (puedes cambiar a datetime si quieres)
    predefined_attrs: Dict[str, dict]
    static_attrs_order: Optional[str] = None
    custom_attrs: Dict[str, dict]
    dynamic_attrs_order: Optional[str] = None
    description: Optional[str] = None
    update_data: Optional[str] = None
    detail_data: Optional[str] = None
    delete_data: Optional[str] = None

class TrapperClassificatorList(BaseModel):
    pagination: Pagination
    results: List[TrapperClassificator]