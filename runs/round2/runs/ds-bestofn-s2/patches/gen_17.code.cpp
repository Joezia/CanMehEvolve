template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* src = values.data() + (fieldArrayIndex * size);
    if (size == sizeof(T))
    {
        T rv;
        std::memcpy(&rv, src, sizeof(T));
        return rv;
    }

    T rv = 0;
    std::memcpy(&rv, src, (size < sizeof(T)) ? size : sizeof(T));
    return rv;
}
