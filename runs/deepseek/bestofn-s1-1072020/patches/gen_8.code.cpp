FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    const FIT_UINT8 type = GetType();
    FIT_FLOAT64 float64Value;

    switch (type) {
        case FIT_BASE_TYPE_BYTE:
        {
            FIT_BYTE v = GetValue<FIT_BYTE>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_BYTE & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_ENUM:
        {
            FIT_ENUM v = GetValue<FIT_ENUM>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_ENUM & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_SINT8:
        {
            FIT_SINT8 v = GetValue<FIT_SINT8>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_SINT8 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT8:
        {
            FIT_UINT8 v = GetValue<FIT_UINT8>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT8 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT8Z:
        {
            FIT_UINT8 v = GetValue<FIT_UINT8>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT8Z & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_SINT16:
        {
            FIT_SINT16 v = GetValue<FIT_SINT16>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_SINT16 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT16:
        {
            FIT_UINT16 v = GetValue<FIT_UINT16>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT16 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT16Z:
        {
            FIT_UINT16 v = GetValue<FIT_UINT16>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT16Z & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_SINT32:
        {
            FIT_SINT32 v = GetValue<FIT_SINT32>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_SINT32 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT32:
        {
            FIT_UINT32 v = GetValue<FIT_UINT32>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT32 & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_UINT32Z:
        {
            FIT_UINT32 v = GetValue<FIT_UINT32>(fieldArrayIndex);
            if (memcmp(&v, baseTypeInvalids[FIT_BASE_TYPE_UINT32Z & FIT_BASE_TYPE_NUM_MASK], sizeof(v)) == 0)
                goto invalid_float64;
            float64Value = static_cast<FIT_FLOAT64>(v);
            break;
        }

        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);

            if (FIT_FLOAT32_INVALID == val)
            {
                return FIT_FLOAT64_INVALID;
            }

            return static_cast<FIT_FLOAT64>(val);
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
            memcpy(&float64Value, &uint64Value, sizeof(FIT_FLOAT64));
            if (memcmp(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0)
            {
                return float64Value;
            }
            break;
        }

        default:
            return FIT_FLOAT64_INVALID;
    }

    return float64Value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

invalid_float64:
    memcpy(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(float64Value));
    return float64Value;
}
