FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 result = type;
    if (result == FIT_UINT8_INVALID)
    {
        const auto p = profile;
        if ((p != NULL) && (profileIndex < p->numFields))
            result = p->fields[profileIndex].type;
    }
    return result;
}
