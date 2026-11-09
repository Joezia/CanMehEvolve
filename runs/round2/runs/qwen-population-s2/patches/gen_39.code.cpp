
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    switch (GetType()) {
        case FIT_BASE_TYPE_BYTE:
        case FIT_BASE_TYPE_ENUM:
        case FIT_BASE_TYPE_SINT8:
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
        {
            FIT_FLOAT64 value = ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            // Avoid memcpy by using union or direct comparison; here we use direct comparison with invalid constant
            // Use the precomputed invalid value from baseTypeInvalids
            const FIT_FLOAT64* invalid = static_cast<const FIT_FLOAT64*>(baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]);
            if (value == *invalid) {
                return value;
            }
            return value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        }

        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            if (val == FIT_FLOAT32_INVALID) {
                return FIT_FLOAT64_INVALID;
            }
            return static_cast<FIT_FLOAT64>(val);
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
            FIT_FLOAT64 value;
            std::memcpy(&value, &uint64Value, sizeof(FIT_FLOAT64));
            
            const FIT_FLOAT64* invalid = static_cast<const FIT_FLOAT64*>(baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]);
            if (value == *invalid) {
                return value;
            }
            return value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        }

        default:
            return FIT_FLOAT64_INVALID;
    }
}
