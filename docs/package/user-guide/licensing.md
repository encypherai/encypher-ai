# Licensing Guide

This guide explains the licensing model for the Encypher Python package, including the implications of the AGPLv3 license and commercial licensing options.

## Open Source License: AGPLv3

The Encypher Python package is licensed under the [GNU Affero General Public License v3.0 (AGPLv3)](https://www.gnu.org/licenses/agpl-3.0.en.html), which is a strong copyleft license designed to ensure that modifications to the software remain open source, even when the software is used to provide a service over a network.

### Key AGPLv3 Provisions

1. **Source Code Access**: Users who receive the software have the right to receive the complete source code, including any modifications.

2. **Network Use Provision**: If you modify the software and use it to provide a service over a network (e.g., a web application), you must make your modified source code available to the users of that service.

3. **Derivative Works**: Any derivative works or modifications must also be licensed under AGPLv3.

4. **Patent Rights**: Contributors grant patent rights to users of the software.

5. **No Additional Restrictions**: You cannot impose additional restrictions on recipients when you redistribute the software.

### What This Means for Users

#### For Open Source Projects

If you're using Encypher in an open source project:

- Your project must also be licensed under AGPLv3 or a compatible license
- You must provide the complete source code, including any modifications to Encypher
- Users of your software must receive these same rights

#### For Internal Use

If you're using Encypher internally within your organization:

- You can freely use and modify the software
- You don't need to publish your modifications as long as the software is only used internally
- If you provide access to the software over a network to users outside your organization, the network use provision applies

#### For SaaS and Web Applications

If you're using Encypher in a SaaS or web application:

- You must make the complete source code, including your modifications, available to users of your service
- This includes providing a prominent offer to download the source code
- This requirement applies even if users don't receive a copy of the software itself

## Commercial Licensing

For organizations that cannot or do not want to comply with the AGPLv3 requirements, Encypher offers commercial licensing options.

### When You Need a Commercial License

You should consider a commercial license if:

1. You want to incorporate Encypher into proprietary software that you distribute to customers
2. You want to use Encypher in a SaaS or web application without making your source code available
3. You need to redistribute Encypher under terms different from AGPLv3
4. You need additional support, indemnification, or warranty beyond what's provided in the open source version

### Commercial License Benefits

- **Proprietary Use**: Incorporate Encypher into your proprietary applications without AGPLv3 obligations
- **Customization**: Make modifications without the requirement to publish your changes
- **Legal Certainty**: Clear licensing terms tailored to your specific use case
- **Support**: Access to priority support and maintenance
- **Indemnification**: Protection against intellectual property claims (depending on license terms)

### Commercial License Types

Encypher offers several types of commercial licenses:

1. **Standard Commercial License**: For embedding in proprietary applications
2. **SaaS License**: For using Encypher in cloud or SaaS offerings
3. **OEM License**: For redistributing Encypher as part of your product
4. **Enterprise License**: Customized licensing for large organizations with specific needs

### How to Obtain a Commercial License

For information about commercial licensing options, pricing, and terms, please contact:

- Email: licensing@encypherai.com
- Website: https://www.encypherai.com/licensing

## Dual Licensing Strategy

Encypher employs a dual licensing strategy:

1. **AGPLv3 for Open Source**: Ensures that improvements to the software remain available to the community
2. **Commercial Licenses for Proprietary Use**: Provides flexibility for commercial applications

This approach allows Encypher to maintain a vibrant open source community while generating revenue to sustain development.

## Frequently Asked Questions

### Can I use Encypher in a commercial project?

Yes, but you have two options:
1. Comply with AGPLv3 requirements, including making your source code available
2. Purchase a commercial license

### Do I need a commercial license for internal use?

If you're only using Encypher internally and not providing access to external users over a network, you can use the AGPLv3 version without publishing your modifications.

### What constitutes a "modification" under AGPLv3?

Any change to the Encypher source code is considered a modification. Simply using the library's API without changing its code is not a modification.

### Can I include Encypher in my open source project under a different license?

No, if you include AGPLv3-licensed code in your project, your entire project must be compatible with AGPLv3.

### Does using Encypher as a dependency require my entire application to be AGPLv3?

Yes, if you distribute your application or make it available over a network. The AGPLv3 is designed to ensure that all code that links to AGPLv3 code is also made available under compatible terms.

## Intellectual Property Considerations

### Patents

Encypher's approach to text provenance using Unicode variation selectors is protected by the AGPLv3 license, which includes patent provisions. Under AGPLv3, contributors grant users a non-exclusive, worldwide, royalty-free patent license for patents they control that would be infringed by the software.

### Contribution to Standards

Encypher is committed to advancing open standards for content provenance. While our implementation is protected by AGPLv3, we actively contribute concepts and approaches to standards bodies like C2PA to promote interoperability and adoption of content provenance technologies.

## Conclusion

The AGPLv3 license provides strong protection for Encypher's innovative approach to text provenance while ensuring that improvements remain available to the community. For users who cannot comply with AGPLv3 requirements, commercial licensing options provide a flexible alternative.

By understanding the implications of our licensing model, you can make informed decisions about how to incorporate Encypher into your projects while respecting intellectual property rights and open source principles.
