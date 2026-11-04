
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid()) {
        return FIT_FLOAT64_INVALID;
    }

    const auto type = GetType();

    // Handle FLOAT64 directly with minimal overhead
    if (type == FIT_BASE_TYPE_FLOAT64) {
        FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
        FIT_FLOAT64 value;
        std::memcpy(&value, &uint64Value, sizeof(FIT_FLOAT64));
        return (value == baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]) ? value : value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
    }

    // Handle FLOAT32 by converting to FLOAT64
    if (type == FIT_BASE_TYPE_FLOAT32) {
        FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
        if (val == FIT_FLOAT32_INVALID) return FIT_FLOAT64_INVALID;
        FIT_FLOAT64 value = static_cast<FIT_FLOAT64>(val);
        return (value == baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]) ? value : value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
    }

    // For all other numeric types, use ConvertBaseType
    switch (type) {
        case FIT_BASE_TYPE_BYTE:
        case FIT_BASE_TYPE_ENUM:
        case FIT_BASE_TYPE_SINT8:
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            {
                FIT_FLOAT64 value = ConvertBaseType<FIT_FLOAT64, FIT_UINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                if (type == FIT_BASE_TYPE_SINT8) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_SINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else if (type == FIT_BASE_TYPE_SINT16) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_SINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else if (type == FIT_BASE_TYPE_SINT32) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_SINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else if (type == FIT_BASE_TYPE_UINT16 || type == FIT_BASE_TYPE_UINT16Z) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_UINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else if (type == FIT_BASE_TYPE_UINT32 || type == FIT_BASE_TYPE_UINT32Z) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_UINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else if (type == FIT_BASE_TYPE_BYTE || type == FIT_BASE_TYPE_ENUM) {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_ENUM>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                } else {
                    value = ConvertBaseType<FIT_FLOAT64, FIT_UINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
                }
                if (value == baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]) {
                    return value;
                }
                return value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
            }
        default:
            return FIT_FLOAT64_INVALID;
    }
}
