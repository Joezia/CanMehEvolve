template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 typeIndex = static_cast<FIT_UINT8>(GetType() & FIT_BASE_TYPE_NUM_MASK);
    const FIT_UINT8 size = baseTypeSizes[typeIndex];

    if (fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[typeIndex]);
    }

    const FIT_UINT8* src = values.data() + (fieldArrayIndex * size);

    T rv = 0;
    if (size <= sizeof(T))
    {
        std::memcpy(&rv, src, size);
    }
    else
    {
        for (FIT_UINT8 i = 0; i < size; i++)
        {
            rv |= static_cast<T>(src[i]) << (i * 8);
        }
    }
    return rv;
}
