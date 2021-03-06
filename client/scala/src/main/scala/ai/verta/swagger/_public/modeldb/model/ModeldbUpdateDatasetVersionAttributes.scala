// THIS FILE IS AUTO-GENERATED. DO NOT EDIT
package ai.verta.swagger._public.modeldb.model

import scala.util.Try

import net.liftweb.json._

import ai.verta.swagger._public.modeldb.model.DatasetTypeEnumDatasetType._
import ai.verta.swagger._public.modeldb.model.DatasetVisibilityEnumDatasetVisibility._
import ai.verta.swagger._public.modeldb.model.OperatorEnumOperator._
import ai.verta.swagger._public.modeldb.model.PathLocationTypeEnumPathLocationType._
import ai.verta.swagger._public.modeldb.model.ProtobufNullValue._
import ai.verta.swagger._public.modeldb.model.ValueTypeEnumValueType._
import ai.verta.swagger.client.objects._

case class ModeldbUpdateDatasetVersionAttributes (
  attribute: Option[CommonKeyValue] = None,
  dataset_id: Option[String] = None,
  id: Option[String] = None
) extends BaseSwagger {
  def toJson(): JValue = ModeldbUpdateDatasetVersionAttributes.toJson(this)
}

object ModeldbUpdateDatasetVersionAttributes {
  def toJson(obj: ModeldbUpdateDatasetVersionAttributes): JObject = {
    new JObject(
      List[Option[JField]](
        obj.attribute.map(x => JField("attribute", ((x: CommonKeyValue) => CommonKeyValue.toJson(x))(x))),
        obj.dataset_id.map(x => JField("dataset_id", JString(x))),
        obj.id.map(x => JField("id", JString(x)))
      ).flatMap(x => x match {
        case Some(y) => List(y)
        case None => Nil
      })
    )
  }

  def fromJson(value: JValue): ModeldbUpdateDatasetVersionAttributes =
    value match {
      case JObject(fields) => {
        val fieldsMap = fields.map(f => (f.name, f.value)).toMap
        ModeldbUpdateDatasetVersionAttributes(
          // TODO: handle required
          attribute = fieldsMap.get("attribute").map(CommonKeyValue.fromJson),
          dataset_id = fieldsMap.get("dataset_id").map(JsonConverter.fromJsonString),
          id = fieldsMap.get("id").map(JsonConverter.fromJsonString)
        )
      }
      case _ => throw new IllegalArgumentException(s"unknown type ${value.getClass.toString}")
    }
}
