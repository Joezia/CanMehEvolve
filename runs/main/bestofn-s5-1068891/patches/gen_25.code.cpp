
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid()) {
        return FIT_FLOAT64_INVALID;
    }

    const FIT_BASE_TYPE type = GetType();
    FIT_FLOAT64 value;

    // Early return for invalid types
    if (type == FIT_BASE_TYPE_FLOAT32) {
        FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
        if (val == FIT_FLOAT32_INVALID) return FIT_FLOAT64_INVALID;
        return static_cast<FIT_FLOAT64>(val);
    }

    if (type == FIT_BASE_TYPE_FLOAT64) {
        FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
        std::memcpy(&value, &uint64Value, sizeof(FIT_FLOAT64));
    } else {
        // Use template specialization via ConvertBaseType for other types
        switch (type) {
            case FIT_BASE_TYPE_BYTE:       value = ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_ENUM:       value = ConvertBaseType<FIT_FLOAT64, FIT_ENUM>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_SINT8:      value = ConvertBaseType<FIT_FLOAT64, FIT_SINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_UINT8:
            case FIT_BASE_TYPE_UINT8Z:     value = ConvertBaseType<FIT_FLOAT64, FIT_UINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_SINT16:     value = ConvertBaseType<FIT_FLOAT64, FIT_SINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_UINT16:
            case FIT_BASE_TYPE_UINT16Z:    value = ConvertBaseType<FIT_FLOAT64, FIT_UINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_SINT32:     value = ConvertBaseType<FIT_FLOAT64, FIT_SINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            case FIT_BASE_TYPE_UINT32:
            case FIT_BASE_TYPE_UINT32Z:    value = ConvertBaseType<FIT_FLOAT64, FIT_UINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64); break;
            default:                       return FIT_FLOAT64_INVALID;
        }
    }

    // Inline invalid check and scale/offset application
    const FIT_FLOAT64* invalidPtr = baseTypeInvalids + (type & FIT_BASE_TYPE_NUM_MASK);
    if (std::memcmp(&value, invalidPtr, sizeof(FIT_FLOAT64)) == 0) {
        return value;
    }

    const FIT_FLOAT64 scale = GetScale(subFieldIndex);
    const FIT_FLOAT64 offset = GetOffset(subFieldIndex);
    return scale != 0.0 ? (value / scale - offset) : value;
}
