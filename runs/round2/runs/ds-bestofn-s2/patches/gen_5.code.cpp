template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];

    if (fieldArrayIndex >= static_cast<FIT_UINT8>(values.size()))
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* src = values.data() + static_cast<size_t>(fieldArrayIndex) * size;

    switch (size)
    {
    case 1:
        return static_cast<T>(src[0]);
    case 2:
    {
        FIT_UINT16 v;
        std::memcpy(&v, src, sizeof(v));
        return static_cast<T>(v);
    }
    case 4:
    {
        FIT_UINT32 v;
        std::memcpy(&v, src, sizeof(v));
        return static_cast<T>(v);
    }
    case 8:
    {
        FIT_UINT64 v;
        std::memcpy(&v, src, sizeof(v));
        return static_cast<T>(v);
    }
    default:
    {
        T rv = 0;
        for (FIT_UINT8 i = 0; i < size; i++)
        {
            rv |= static_cast<T>(src[i]) << (i * 8);
        }
        return rv;
    }
    }
}
