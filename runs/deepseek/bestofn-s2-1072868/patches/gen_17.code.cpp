template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    const FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    const FIT_UINT8 size = baseTypeSizes[type];
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* p = values.data() + (fieldArrayIndex * size);
    T rv = 0;

    if (size <= sizeof(T))
    {
        switch (size)
        {
        case 0:
            break;
        case 1:
            rv = static_cast<T>(p[0]);
            break;
        case 2:
            std::memcpy(&rv, p, 2);
            break;
        case 4:
            std::memcpy(&rv, p, 4);
            break;
        case 8:
            std::memcpy(&rv, p, 8);
            break;
        default:
            std::memcpy(&rv, p, size);
            break;
        }
        return rv;
    }

    for (int i = 0; i < size; i++)
    {
        rv |= static_cast<T>(values[(fieldArrayIndex * size) + i]) << (i * 8);
    }

    return rv;
}
