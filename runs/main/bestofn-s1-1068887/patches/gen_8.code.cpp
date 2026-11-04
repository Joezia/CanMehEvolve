
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    switch (GetType()) {
        case FIT_BASE_TYPE_FLOAT64: {
            FIT_UINT64 uint64Value = GetValue<FIT_UINT64>(fieldArrayIndex);
            FIT_FLOAT64 val;
            std::memcpy(&val, &uint64Value, sizeof(FIT_FLOAT64));
            return (val != *reinterpret_cast<const FIT_FLOAT64*>(baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK]))
                   ? (val / GetScale(subFieldIndex) - GetOffset(subFieldIndex)) : val;
        }
        case FIT_BASE_TYPE_FLOAT32: {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            return (val != FIT_FLOAT32_INVALID) ? static_cast<FIT_FLOAT64>(val) : FIT_FLOAT64_INVALID;
        }
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
            return ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        default:
            return FIT_FLOAT64_INVALID;
    }
}
