
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    FIT_FLOAT64 float64Value;

    switch (GetType()) {
        case FIT_BASE_TYPE_BYTE:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_ENUM:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_ENUM>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_SINT8:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_SINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_UINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_SINT16:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_SINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_UINT16:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_UINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_SINT32:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_SINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_UINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_FLOAT32: {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            if (val == FIT_FLOAT32_INVALID) {
                return FIT_FLOAT64_INVALID;
            }
            float64Value = static_cast<FIT_FLOAT64>(val);
            break;
        }
        case FIT_BASE_TYPE_FLOAT64: {
            FIT_FLOAT64 val = GetValue<FIT_FLOAT64>(fieldArrayIndex);
            float64Value = val;
            break;
        }
        default:
            return FIT_FLOAT64_INVALID;
    }

    // Direct invalid check for FLOAT64 (NaN check is more efficient than memcmp)
    if (float64Value != float64Value) { // NaN check: NaN != NaN is true
        return float64Value;
    }

    const FIT_FLOAT64 scale = GetScale(subFieldIndex);
    const FIT_FLOAT64 offset = GetOffset(subFieldIndex);
    
    // Only apply scale/offset if necessary (avoid expensive division when scale=1.0 and offset=0.0)
    if (scale != 1.0 || offset != 0.0) {
        float64Value = float64Value / scale - offset;
    }

    return float64Value;
}
