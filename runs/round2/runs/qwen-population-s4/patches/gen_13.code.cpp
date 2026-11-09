
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
        {
            FIT_FLOAT64 val = ConvertBaseType<FIT_FLOAT64, FIT_BYTE>(fieldArrayIndex, FIT_BASE_TYPE_FLOAT64);
            return (memcmp(&val, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0) 
                   ? val 
                   : val / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        }

        case FIT_BASE_TYPE_FLOAT32:
        {
            FIT_FLOAT32 f32 = GetFLOAT32Value(fieldArrayIndex, subFieldIndex);
            if (f32 == FIT_FLOAT32_INVALID) return FIT_FLOAT64_INVALID;
            return static_cast<FIT_FLOAT64>(f32);
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            FIT_FLOAT64 val;
            std::memcpy(&val, &data_[fieldArrayIndex * sizeof(FIT_FLOAT64)], sizeof(FIT_FLOAT64));
            if (memcmp(&val, baseTypeInvalids[FIT_BASE_TYPE_FLOAT64 & FIT_BASE_TYPE_NUM_MASK], sizeof(FIT_FLOAT64)) == 0)
                return val;
            return val / GetScale(subFieldIndex) - GetOffset(subFieldIndex);
        }

        default:
            return FIT_FLOAT64_INVALID;
    }
}
