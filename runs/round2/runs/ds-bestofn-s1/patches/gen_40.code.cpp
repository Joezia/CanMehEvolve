FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 t = type;
    if ( t != FIT_UINT8_INVALID )
        return t;

    const auto p = profile;
    if ( (p != NULL) && (profileIndex < p->numFields) )
        return p->fields[profileIndex].type;

    return FIT_UINT8_INVALID;
}
