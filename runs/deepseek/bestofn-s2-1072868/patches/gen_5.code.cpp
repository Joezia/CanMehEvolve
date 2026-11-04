template <typename TTo, typename TFrom>
TTo FieldBase::ConvertBaseType(const FIT_UINT8 fieldArrayIndex, const FIT_UINT8 toBaseType) const
{
    FIT_CONST_UINT8_PTR invalid = baseTypeInvalids[GetType() & FIT_BASE_TYPE_NUM_MASK];
    TFrom value = GetValue<TFrom>(fieldArrayIndex);

    bool isInvalid;
    if constexpr (sizeof(TFrom) <= sizeof(FIT_UINT64))
    {
        FIT_UINT64 valueBits = 0;
        FIT_UINT64 invalidBits = 0;
        std::memcpy(&valueBits, &value, sizeof(TFrom));
        std::memcpy(&invalidBits, invalid, sizeof(TFrom));
        isInvalid = (valueBits == invalidBits);
    }
    else
    {
        isInvalid = (std::memcmp(&value, invalid, sizeof(TFrom)) == 0);
    }

    if (isInvalid)
        return *reinterpret_cast<const TTo*>(baseTypeInvalids[toBaseType & FIT_BASE_TYPE_NUM_MASK]);

    return static_cast<TTo>(value);
}
