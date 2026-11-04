
FIT_FLOAT64 FieldBase::GetFLOAT64Value(const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex) const
{
    if (!IsValid())
        return FIT_FLOAT64_INVALID;

    const FIT_BASE_TYPE type = GetType();

    switch (type)
    {
        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 val = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            return (val == FIT_FLOAT32_INVALID) ? FIT_FLOAT64_INVALID : static_cast<FIT_FLOAT64>(val);
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            if (fieldArrayIndex >= GetSize() / sizeof(FIT_FLOAT64))
                return FIT_FLOAT64_INVALID;
            FIT_FLOAT64 value;
            std::memcpy(&value, &data_[fieldArrayIndex * sizeof(FIT_FLOAT64)], sizeof(FIT_FLOAT64));
            if (std::memcmp(&value, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0)
                return value;
            return value / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        }

        case FIT_BASE_TYPE_BYTE:
            return ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_ENUM:
            return ConvertBaseType<FIT_FLOAT64, FIT_ENUM>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_SINT8:
            return ConvertBaseType<FIT_FLOAT64, FIT_SINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
            return ConvertBaseType<FIT_FLOAT64, FIT_UINT8>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_SINT16:
            return ConvertBaseType<FIT_FLOAT64, FIT_SINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_UINT16Z:
        case FIT_BASE_TYPE_UINT16:
            return ConvertBaseType<FIT_FLOAT64, FIT_UINT16>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_SINT32:
            return ConvertBaseType<FIT_FLOAT64, FIT_SINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
            return ConvertBaseType<FIT_FLOAT64, FIT_UINT32>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64) / GetScale(subFieldIndex) - GetOffset(subFieldIndex);

        default:
            return FIT_FLOAT64_INVALID;
    }
}
