
template <typename T>
T FieldBase::GetValue(const FIT_UINT8 fieldArrayIndex) const
{
    FIT_UINT8 type = GetType() & FIT_BASE_TYPE_NUM_MASK;
    FIT_UINT8 size = baseTypeSizes[type];
    
    if (fieldArrayIndex >= (FIT_UINT8)values.size())
    {
        return *reinterpret_cast<const T*>(baseTypeInvalids[type]);
    }

    const FIT_UINT8* data = &values[(fieldArrayIndex * size)];
    if (std::is_trivially_copyable<T>::value && sizeof(T) <= 8)
    {
        T rv;
        std::memcpy(&rv, data, size);
        return rv;
    }
    else
    {
        T rv = 0;
        std::memcpy(&rv, data, size);
        return rv;
    }
}
