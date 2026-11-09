FIT_UINT8 Field::GetType() const
{
    if ( type != FIT_UINT8_INVALID )
        return type;

    const Profile* const p = profile;
    return ( p != NULL && profileIndex < p->numFields )
               ? p->fields[profileIndex].type
               : FIT_UINT8_INVALID;
}
