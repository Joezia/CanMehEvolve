FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;

    return (profile && (profileIndex < profile->numFields))
        ? profile->fields[profileIndex].type
        : FIT_UINT8_INVALID;
}
