FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 cachedType = type;
    if (__builtin_expect(cachedType == FIT_UINT8_INVALID, 0))
    {
        const Profile::MESG* const p = profile;
        if (__builtin_expect(p != NULL, 1))
        {
            const FIT_UINT8 index = profileIndex;
            if (__builtin_expect(index < p->numFields, 1))
            {
                cachedType = p->fields[index].type;
                const_cast<FIT_UINT8&>(type) = cachedType;
            }
        }
    }
    return cachedType;
}
