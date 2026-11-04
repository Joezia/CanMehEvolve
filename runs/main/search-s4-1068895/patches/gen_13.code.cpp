
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    const auto type = GetType();
    FIT_FLOAT64 float64Value;

    // Fast path: FLOAT64 base type - direct memcpy
    if (type == FIT_BASE_TYPE_FLOAT64) {
        FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
        std::memcpy(&float64Value, &uint64Value, sizeof(FIT_FLOAT64));
        // Check for invalid value inline (avoid function call)
        if (std::memcmp(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0) {
            return float64Value;
        }
        return float64Value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
    }

    // Special handling for FLOAT32 to avoid conversion overhead
    if (type == FIT_BASE_TYPE_FLOAT32) {
        FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
        if (val == FIT_FLOAT32_INVALID) {
            return FIT_FLOAT64_INVALID;
        }
        float64Value = static_cast<FIT_FLOAT64>(val);
        if (std::memcmp(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0) {
            return float64Value;
        }
        return float64Value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
    }

    // Handle other numeric types via ConvertBaseType (unrolled for performance)
    switch (type) {
        case FIT_BASE_TYPE_BYTE:
        case FIT_BASE_TYPE_ENUM:
        case FIT_BASE_TYPE_SINT8:
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_UINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            float64Value = ConvertBaseType<FIT_FLOAT64, FIT_UINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            break;
        default:
            return FIT_FLOAT64_INVALID;
    }

    // Inline invalid check to avoid function call overhead
    if (std::memcmp(&float64Value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0) {
        return float64Value;
    }

    return float64Value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
}
