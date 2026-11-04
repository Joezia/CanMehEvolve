Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    Field* f = fields.data();
    Field* const end = f + fields.size();
    for (; f != end; ++f)
    {
        if (f->GetNum() == fieldNum)
            return f;
    }

    return FIT_NULL;
}
