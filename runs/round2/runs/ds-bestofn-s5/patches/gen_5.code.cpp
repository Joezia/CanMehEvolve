FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    FIT_FLOAT64 float64Value;

    switch (GetType()) {
        case FIT_BASE_TYPE_BYTE:
        {
            FIT_BYTE value = GetValue<FIT_BYTE>(fieldArrayIndex);
            if (value == FIT_BYTE_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_ENUM:
        {
            FIT_ENUM value = GetValue<FIT_ENUM>(fieldArrayIndex);
            if (value == FIT_ENUM_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_SINT8:
        {
            FIT_SINT8 value = GetValue<FIT_SINT8>(fieldArrayIndex);
            if (value == FIT_SINT8_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
        {
            FIT_UINT8 value = GetValue<FIT_UINT8>(fieldArrayIndex);
            if (value == FIT_UINT8_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_SINT16:
        {
            FIT_SINT16 value = GetValue<FIT_SINT16>(fieldArrayIndex);
            if (value == FIT_SINT16_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_UINT16:
        {
            FIT_UINT16 value = GetValue<FIT_UINT16>(fieldArrayIndex);
            if (value == FIT_UINT16_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_SINT32:
        {
            FIT_SINT32 value = GetValue<FIT_SINT32>(fieldArrayIndex);
            if (value == FIT_SINT32_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
        {
            FIT_UINT32 value = GetValue<FIT_UINT32>(fieldArrayIndex);
            if (value == FIT_UINT32_INVALID)
                return FIT_FLOAT64_INVALID;
            float64Value = static_cast<FIT_FLOAT64>(value);
            break;
        }
        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            if (FIT_FLOAT32_INVALID == val)
                return FIT_FLOAT64_INVALID;
            return static_cast<FIT_FLOAT64>(val);
        }
        case FIT_BASE_TYPE_FLOAT64:
        {
            FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
            memcpy(&float64Value, &uint64Value, sizeof(FIT_FLOAT64));
            if (memcmp(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0)
                return float64Value;
            break;
        }
        default:
            return FIT_FLOAT64_INVALID;
    }

    FIT_FLOAT64 scale = GetScale(subFieldIndex);
    if (scale != 1.0)
    {
        float64Value /= scale;
    }

    return float64Value - GetOffset(subFieldIndex);
}
