void Mesg::SetFieldSINT16Value(const FIT_UINT8 fieldNum, const FIT_SINT16 value, const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex)
{
    if (subFieldIndex != FIT_SUBFIELD_INDEX_MAIN_FIELD)
    {
        auto mesgProfile = Profile::GetMesg(mesgNum);
        if (mesgProfile == FIT_NULL)
            return;

        auto fieldProfile = Profile::GetMesgField(mesgProfile, fieldNum);
        if (fieldProfile == FIT_NULL)
            return;

        if (subFieldIndex >= fieldProfile->numSubFields)
            return;

        auto fieldIterator = fields.lower_bound(fieldNum);
        if (fieldIterator != fields.end() && fieldIterator->first == fieldNum)
        {
            fieldIterator->second.SetSINT16Value(value, fieldArrayIndex);
            return;
        }

        Field field(fieldNum, *fieldProfile);
        fieldIterator = fields.emplace_hint(fieldIterator, fieldNum, field);
        fieldIterator->second.SetSINT16Value(value, fieldArrayIndex);
        return;
    }

    auto fieldIterator = fields.lower_bound(fieldNum);
    if (fieldIterator != fields.end() && fieldIterator->first == fieldNum)
    {
        fieldIterator->second.SetSINT16Value(value, fieldArrayIndex);
        return;
    }

    auto mesgProfile = Profile::GetMesg(mesgNum);
    if (mesgProfile == FIT_NULL)
        return;

    auto fieldProfile = Profile::GetMesgField(mesgProfile, fieldNum);
    if (fieldProfile == FIT_NULL)
        return;

    Field field(fieldNum, *fieldProfile);
    fieldIterator = fields.emplace_hint(fieldIterator, fieldNum, field);
    fieldIterator->second.SetSINT16Value(value, fieldArrayIndex);
}
