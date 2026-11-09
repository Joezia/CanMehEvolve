FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;

    const FIT_PROFILE* p = profile;
    if (p && profileIndex < p->numFields)
        return p->fields[profileIndex].type;

    return FIT_UINT8_INVALID;
}
