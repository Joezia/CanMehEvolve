void Mesg::SetFieldSINT16Value(const FIT_UINT8 fieldNum, const FIT_SINT16 value, const FIT_UINT8 fieldArrayIndex, const FIT_UINT16 subFieldIndex)
{
    if (subFieldIndex != FIT_SUBFIELD_INDEX_MAIN_FIELD)
    {
        auto mesgProfile = Profile::GetMesg(GetNum());
        if (mesgProfile == FIT_NULL)
            return;

        auto fieldProfile = Profile::GetField(mesgProfile, fieldNum);
        if (fieldProfile == FIT_NULL)
            return;

        if (subFieldIndex >= fieldProfile->numSubFields)
            return;

        for (auto &field : fields)
        {
            if (field.GetNum() == fieldNum)
            {
                field.SetSINT16Value(value, fieldArrayIndex);
                return;
            }
        }

        fields.push_back(Field(fieldNum, *fieldProfile));
        fields.back().SetSINT16Value(value, fieldArrayIndex);
        return;
    }

    for (auto &field : fields)
    {
        if (field.GetNum() == fieldNum)
        {
            field.SetSINT16Value(value, fieldArrayIndex);
            return;
        }
    }

    auto mesgProfile = Profile::GetMesg(GetNum());
    if (mesgProfile == FIT_NULL)
        return;

    auto fieldProfile = Profile::GetField(mesgProfile, fieldNum);
    if (fieldProfile == FIT_NULL)
        return;

    fields.push_back(Field(fieldNum, *fieldProfile));
    fields.back().SetSINT16Value(value, fieldArrayIndex);
}
