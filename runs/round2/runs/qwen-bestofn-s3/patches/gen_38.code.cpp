
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
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            return ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);

        case FIT_BASE_TYPE_FLOAT32: {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            return (val == FIT_FLOAT32_INVALID) ? FIT_FLOAT64_INVALID : static_cast<FIT_FLOAT64>(val);
        }

        case FIT_BASE_TYPE_FLOAT64: {
            FIT_FLOAT64 value;
            std::memcpy(&value, &data_[fieldArrayIndex * sizeof(FIT_FLOAT64)], sizeof(FIT_FLOAT64));
            return value;
        }

        default:
            return FIT_FLOAT64_INVALID;
    }
}
