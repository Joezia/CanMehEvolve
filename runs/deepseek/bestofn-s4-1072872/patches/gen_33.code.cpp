template <typename TTo, typename TFrom>
TTo FieldBase::ConvertBaseType(const FIT_UINT8 fieldArrayIndex, const FIT_UINT8 toBaseType) const
{
    const FIT_UINT8* invalid = baseTypeInvalids[type & FIT_BASE_TYPE_NUM_MASK];
    const FIT_UINT8* src = &field[fieldArrayIndex];
    TFrom value;
    std::memcpy(&value, src, sizeof(TFrom));

    bool isInvalid;
    if constexpr (std::is_floating_point<TFrom>::value) {
        if constexpr (sizeof(TFrom) == 4) {
            FIT_UINT32 v, i;
            std::memcpy(&v, &value, 4);
            std::memcpy(&i, invalid, 4);
            isInvalid = (v == i);
        } else if constexpr (sizeof(TFrom) == 8) {
            FIT_UINT64 v, i;
            std::memcpy(&v, &value, 8);
            std::memcpy(&i, invalid, 8);
            isInvalid = (v == i);
        } else {
            isInvalid = (std::memcmp(&value, invalid, sizeof(TFrom)) == 0);
        }
    } else {
        TFrom invalidValue;
        std::memcpy(&invalidValue, invalid, sizeof(TFrom));
        isInvalid = (value == invalidValue);
    }

    if (isInvalid)
        return *reinterpret_cast<const TTo*>(baseTypeInvalids[toBaseType & FIT_BASE_TYPE_NUM_MASK]);

    return static_cast<TTo>(value);
}
