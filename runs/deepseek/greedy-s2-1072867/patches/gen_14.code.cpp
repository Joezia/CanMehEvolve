FIT_UINT8 Field::GetType() const
{
    if ( type != FIT_UINT8_INVALID )
        return type;

    const Profile* const p = profile;
    if ( p != NULL && profileIndex < p->numFields )
        return p->fields[profileIndex].type;

    return type;
}
