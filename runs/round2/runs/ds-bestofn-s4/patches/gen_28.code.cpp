FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 cachedType = type;

    if (cachedType == FIT_UINT8_INVALID)
    {
        const auto p = profile;
        if ((p != NULL) && (profileIndex < p->numFields))
            return p->fields[profileIndex].type;
    }

    return cachedType;
}
