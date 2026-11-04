template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 baseType = static_cast<FIT_UINT8>(GetType() & FIT_BASE_TYPE_NUM_MASK);

    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[baseType]);
    }

    const FIT_UINT8 size = baseTypeSizes[baseType];
    const FIT_UINT8* p = values.data() + static_cast<size_t>(fieldArrayIndex) * size;

    switch (size)
    {
        case 1:
            return static_cast<T>(p[0]);
        case 2:
        {
            FIT_UINT16 v;
            std::memcpy(&v, p, sizeof(v));
            return static_cast<T>(v);
        }
        case 4:
        {
            FIT_UINT32 v;
            std::memcpy(&v, p, sizeof(v));
            return static_cast<T>(v);
        }
        case 8:
        {
            FIT_UINT64 v;
            std::memcpy(&v, p, sizeof(v));
            return static_cast<T>(v);
        }
        default:
        {
            T rv = 0;
            for (int i = 0; i < size; i++)
            {
                rv |= static_cast<T>(p[i]) << (i * 8);
            }
            return rv;
        }
    }
}
