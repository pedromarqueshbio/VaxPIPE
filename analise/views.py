from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from analise import limpar
from analise.forms import Parametros
from Bio import SeqIO
import analise.scriptPedro as sp


class Dados(FormView):
    form_class = Parametros
    template_name = 'dados.html'
    success_url = reverse_lazy('recebido')

    def salvarfasta(self, fasta):
        with open('epitopos/uploads/'+fasta.name, 'wb+') as destination:
            for chunk in fasta.chunks():
                destination.write(chunk)

    def lerarquivo(self, arquivo):
        proteinslist = []
        for protein in SeqIO.parse(f'{arquivo}', 'fasta'):
            t = (str(protein.id), str(protein.seq))
            proteinslist.append(t)
        return proteinslist


    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = Parametros(request.POST, request.FILES)
            if form.is_valid():
                if not 'proteinfile' in request.FILES:
                    proteinsseqfile = form.cleaned_data['proteinsequence']
                    self.request.session['proteinsseqfile'] = proteinsseqfile
                else:
                    self.salvarfasta(request.FILES['proteinfile'])
                    proteinsseqfile = self.lerarquivo(f"epitopos/uploads/{request.FILES['proteinfile']}")
                    self.request.session['proteinsseqfile'] = proteinsseqfile
                analysisname = form.cleaned_data['analysisname']
                adjuvant = form.cleaned_data['adjuvant']
                mhcI = form.cleaned_data['mhcI']
                mhcII = form.cleaned_data['mhcII']
                mhcILinker = form.cleaned_data['mhcILinker']
                mhcIILinker = form.cleaned_data['mhcIILinker']
                chimericmodelsnumber = form.cleaned_data['chimericmodelsnumber']
                sizeMHCIepitopes = form.cleaned_data['sizeMHCIepitopes']
                sizeMHCIIepitopes = form.cleaned_data['sizeMHCIIepitopes']
                methodsMHCI = form.cleaned_data['methodsMHCI']
                methodsMHCII = form.cleaned_data['methodsMHCII']
                IC50MHCI = form.cleaned_data['IC50MHCI']
                IC50MHCII = form.cleaned_data['IC50MHCII']
                p1 = form.cleaned_data['p1']
                p2 = form.cleaned_data['p2']
                email = form.cleaned_data['email']
                with open('email.str', 'w') as file:
                    file.write(email)
                with open ('analysisname.str', 'w') as file:
                    file.write (analysisname)
                # sessions
                self.request.session['analysisname'] = analysisname
                self.request.session['adjuvant'] = adjuvant
                self.request.session['mhcI'] = mhcI
                self.request.session['mhcII'] = mhcII
                self.request.session['mhcILinker'] = mhcILinker
                self.request.session['mhcIILinker'] = mhcIILinker
                self.request.session['chimericmodelsnumber'] = chimericmodelsnumber
                self.request.session['sizeMHCIepitopes'] = sizeMHCIepitopes
                self.request.session['sizeMHCIIepitopes'] = sizeMHCIIepitopes
                self.request.session['methodsMHCI'] = methodsMHCI
                self.request.session['methodsMHCII'] = methodsMHCII
                self.request.session['IC50MHCI'] = IC50MHCI
                self.request.session['IC50MHCII'] = IC50MHCII
                self.request.session['p1'] = p1
                self.request.session['p2'] = p2
                self.request.session['email'] = email

                return super().form_valid(form)
            else:
                # Se o formulário não for válido, renderiza o formulário com os erros
                return render(request, 'dados.html', {'form': form})
        else:
            form = Parametros()
            # Se a solicitação não for POST, renderiza o formulário vazio
            return render(request, 'dados.html', {'form': form})


class Analisar(TemplateView):
    template_name = 'recebidos.html'

    def get_context_data(self, **kwargs):
        context = super(Analisar, self).get_context_data(**kwargs)
        #
        analysisnameform = self.request.session['analysisname']
        adjuvantform = self.request.session['adjuvant']
        mhcIform = self.request.session['mhcI']
        mhcIIform = self.request.session['mhcII']
        mhcILinkerform = self.request.session['mhcILinker']
        mhcIILinkerform = self.request.session['mhcIILinker']
        chimericmodelsnumberform = self.request.session['chimericmodelsnumber']
        sizeMHCIepitopesform = self.request.session['sizeMHCIepitopes']
        sizeMHCIIepitopesform = self.request.session['sizeMHCIIepitopes']
        methodsMHCIform = self.request.session['methodsMHCI']
        methodsMHCIIform = self.request.session['methodsMHCII']
        IC50MHCIform = self.request.session['IC50MHCI']
        IC50MHCIIform = self.request.session['IC50MHCII']
        p1form = self.request.session['p1']
        p2form = self.request.session['p2']
        emailform = self.request.session['email']
        proteinsseqfileform = self.request.session['proteinsseqfile']
        #
        context['analysisnameform'] = analysisnameform
        context['adjuvantform'] = adjuvantform
        context['mhcIform'] = mhcIform
        context['mhcIIform'] = mhcIIform
        context['mhcILinkerform'] = mhcILinkerform
        context['mhcIILinkerform'] = mhcIILinkerform
        context['chimericmodelsnumberform'] = chimericmodelsnumberform
        context['sizeMHCIepitopesform'] = sizeMHCIepitopesform
        context['sizeMHCIIepitopesform'] = sizeMHCIIepitopesform
        context['methodsMHCIform'] = methodsMHCIform
        context['methodsMHCIIform'] = methodsMHCIIform
        context['IC50MHCIform'] = IC50MHCIform
        context['IC50MHCIIform'] = IC50MHCIIform
        context['p1form'] = p1form
        context['p2form'] = p2form
        context['emailform'] = emailform
        context['proteinsseqfileform'] = proteinsseqfileform
        data_dict = {'analysisnameform': analysisnameform,
                    'emailform': emailform,
                    'proteinsseqfileform': proteinsseqfileform,
                    'mhcIform': mhcIform,
                    'mhcIIform': mhcIIform,
                    'methodsMHCIform': methodsMHCIform,
                    'methodsMHCIIform': methodsMHCIIform,
                    'tmMHCI': sizeMHCIepitopesform,
                    'tmMHCII': sizeMHCIIepitopesform,
                    'p1form': p1form,
                    'p2form': p2form,
                    'IC50MHCIform': IC50MHCIform,
                    'IC50MHCIIform': IC50MHCIIform,
                    'chimericmodelsnumberform': chimericmodelsnumberform,
                    'mhcILinkerform': mhcILinkerform,
                    'mhcIILinkerform': mhcIILinkerform,
                    'adjuvantform': adjuvantform}

        a = sp.dataform(data_dict)
        
        sp.predicao(a)

        limpar.enviar_email()
        limpar.apagar_arquivos()

        return context
